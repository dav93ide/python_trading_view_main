import wx
import requests
import io
from Classes.Cryptocurrency import Cryptocurrency

class CryptosViewList(wx.ListCtrl):

    LIST_COLUMNS = ["%", "Symbol", "Price"]
    LIST_COLUMNS_SIZES = [75, 250, 100]

    __mCallback = None
    __mFilterData = None
    __mFilterName = None
    __mItems: [Cryptocurrency] = None
    __mFilteredItems: [Cryptocurrency] = None

    def __init__(self, parent, id, style, width, callback):
        wx.ListCtrl.__init__(self, parent, id, style=style)
        self.__mCallback = callback
        self.__mWidth = width
        self.__mItems = []

#region - Get Methods
    def get_items(self):
        return self.__mItems

    def set_items(self, items):
        self.__mItems = items

    def get_filtered_items(self):
        return self.__mFilteredItems

    def add_item(self, item):
        self.__mItems.append(item)
#endregion

#region - Set Methods
    def set_filter_data(self, filter):
        self.__mFilterData = filter
#enderegion

#region - Public Methods
    def init_layout(self):
        for i in range(0, len(self.LIST_COLUMNS_SIZES)):
            self.InsertColumn(i, self.LIST_COLUMNS[i])
            self.SetColumnWidth(i, self.LIST_COLUMNS_SIZES[i])

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)

    def get_item_position(self, item):
        for i in range(0, len(self.__mFilteredItems)):
            item = self.__mFilteredItems[i]
            if item.get_id() == item.get_id():
                return i
        return -1

    def get_filtered_item_position(self, item):
        for i in range(0, len(self.__mFilteredItems)):
            item = self.__mFilteredItems[i]
            if item.get_id() == item.get_id():
                return i
        return -1

    def add_items_and_populate(self, items):
        self.__mItems = items
        self.__mFilteredItems = items
        self.filter_items()
        self.populate_list()

    def add_specific_filtered_items(self, items, start, end):
        j = 0
        for i in range(start, end):
            self.__mFilteredItems[i] = items[j]
            item = self.__mFilteredItems[i]
            j += 1
            if j >= len(items):
                break

    def populate_list(self):
        self.DeleteAllItems()
        if self.__mFilteredItems:
            for i in range(0, len(self.__mFilteredItems)):
                item = self.__mFilteredItems[i]
                if item.get_market_change_percent() is not None and float(item.get_market_change_percent()) > 0:
                    self.InsertItem(i, "+" + str(round(float(item.get_market_change_percent()), 2)))
                else:
                    if item.get_market_change_percent() is not None:
                        self.InsertItem(i, str(round(float(item.get_market_change_percent()), 2)))
                    else:
                        self.InsertItem(i, str(0))  
                self.SetItem(i, 1, str(item.get_sign()))
                self.SetItem(i, 2, str(item.get_price()))

    def on_item_selected(self, event):
        if self.__mCallback is not None:
            self.__mCurrentItem = self.__mFilteredItems[event.Index]
            self.__mCallback(self.__mCurrentItem)

    def filter_items_by_name(self, ffilter):
        self.__mFilterName = ffilter
        self.filter_items()

    def filter_items(self):
        for item in self.__mItems:
            if item.get_market_change_percent() is None:
                item.set_market_change_percent(0)
            if item.get_volume() is None:
                item.set_volume(0) 
        self.filter_name()
        if self.__mFilterData is not None:
            self.filter_values()
            self.filter_order()
        self.populate_list()

    def filter_name(self):
        if self.__mFilterName:
            self.__mFilteredItems = []
            for item in self.__mItems:
                if self.__mFilterName.lower() in item.get_sign().lower():
                    self.__mFilteredItems.append(item)
        else:
            self.__mFilteredItems = self.__mItems

    def filter_order(self):
        if self.__mFilterData.get_max_price_mover():
            pos = -1
            for i in range(0, len(self.__mFilteredItems)):
                one = self.__mFilteredItems[i]
                for j in range(i + 1, len(self.__mFilteredItems)):
                    two = self.__mFilteredItems[j]
                    if one.get_market_change_percent() < two.get_market_change_percent():
                        one = two
                        pos = j
                temp = self.__mFilteredItems[i]
                self.__mFilteredItems[i] = one
                self.__mFilteredItems[pos] = temp

        if self.__mFilterData.get_min_price_mover():
            pos = -1
            for i in range(0, len(self.__mFilteredItems)):
                one = self.__mFilteredItems[i]
                for j in range(i + 1, len(self.__mFilteredItems)):
                    two = self.__mFilteredItems[j]
                    if one.get_market_change_percent() > two.get_market_change_percent():
                        one = two
                        pos = j
                temp = self.__mFilteredItems[i]
                self.__mFilteredItems[i] = one
                self.__mFilteredItems[pos] = temp

        if self.__mFilterData.get_max_volume_mover():
            pos = -1
            for i in range(0, len(self.__mFilteredItems)):
                one = self.__mFilteredItems[i]
                for j in range(i + 1, len(self.__mFilteredItems)):
                    two = self.__mFilteredItems[j]
                    if one.get_volume() < two.get_volume():
                        one = two
                        pos = j
                temp = self.__mFilteredItems[i]
                self.__mFilteredItems[i] = one
                self.__mFilteredItems[pos] = temp

        if self.__mFilterData.get_min_volume_mover():
            pos = -1
            for i in range(0, len(self.__mFilteredItems)):
                one = self.__mFilteredItems[i]
                for j in range(i + 1, len(self.__mFilteredItems)):
                    two = self.__mFilteredItems[j]
                    if one.get_volume() > two.get_volume():
                        one = two
                        pos = j
                temp = self.__mFilteredItems[i]
                self.__mFilteredItems[i] = one
                self.__mFilteredItems[pos] = temp

    def filter_values(self):
        if self.__mFilterData is not None:
            items = []
            for item in self.__mFilteredItems:

                if self.__mFilterData.get_max_price() is not None and self.__mFilterData.get_max_price() and self.__mFilterData.get_min_price() is not None and self.__mFilterData.get_min_price():
                    if item.get_price() >= float(self.__mFilterData.get_min_price()) and item.get_price() <= float(self.__mFilterData.get_max_price()):
                        items.append(item)
                elif self.__mFilterData.get_min_price() is not None and self.__mFilterData.get_min_price():
                    if item.get_price() >= float(self.__mFilterData.get_min_price()):
                        items.append(item)
                elif self.__mFilterData.get_max_price() is not None and self.__mFilterData.get_max_price():
                    if item.get_price() <= float(self.__mFilterData.get_max_price()):
                        items.append(item)
                        

                if self.__mFilterData.get_min_volume() is not None and self.__mFilterData.get_min_volume() and self.__mFilterData.get_max_volume() is not None and self.__mFilterData.get_max_volume():
                    if item.get_volume() >= float(self.__mFilterData.get_min_volume()) and item.get_volume() <= float(self.__mFilterData.get_max_volume()):
                        items.append(item)
                elif self.__mFilterData.get_min_volume() is not None and self.__mFilterData.get_min_volume():
                    if item.get_volume() >= float(self.__mFilterData.get_min_volume()):
                        items.append(item)
                elif self.__mFilterData.get_max_volume() is not None and self.__mFilterData.get_max_volume():
                    if item.get_volume() <= float(self.__mFilterData.get_max_volume()):
                        items.append(item)

                if self.__mFilterData.get_value_max_mover() is not None and self.__mFilterData.get_value_max_mover() and self.__mFilterData.get_value_min_mover() is not None and self.__mFilterData.get_value_min_mover():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= float(self.__mFilterData.get_value_max_mover()) and float(item.get_market_change_percent()) >= float(self.__mFilterData.get_value_min_mover()):
                        items.append(item)
                elif self.__mFilterData.get_value_min_mover() is not None and self.__mFilterData.get_value_min_mover():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= float(self.__mFilterData.get_value_min_mover()):
                        items.append(item)
                elif self.__mFilterData.get_value_max_mover() is not None and self.__mFilterData.get_value_max_mover():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= float(self.__mFilterData.get_value_max_mover()):
                        items.append(item)


                if self.__mFilterData.get_mover_above_zero() is not None and self.__mFilterData.get_mover_above_zero():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 0:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_above_fifty() is not None and self.__mFilterData.get_mover_above_fifty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 50:
                        items.append(item)

                if self.__mFilterData.get_mover_above_hundred() is not None and self.__mFilterData.get_mover_above_hundred():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 100:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_below_zero() is not None and self.__mFilterData.get_mover_below_zero():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= 0:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_below_fifty() is not None and self.__mFilterData.get_mover_below_fifty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= -50:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_above_zero_to_ten() is not None and self.__mFilterData.get_mover_above_zero_to_ten():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 0 and float(item.get_market_change_percent()) <= 10:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_above_ten_to_twenty() is not None and self.__mFilterData.get_mover_above_ten_to_twenty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 10 and float(item.get_market_change_percent()) <= 20:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_above_twenty_to_thirty() is not None and self.__mFilterData.get_mover_above_twenty_to_thirty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 20 and float(item.get_market_change_percent()) <= 30:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_above_thirty_to_fourty() is not None and self.__mFilterData.get_mover_above_thirty_to_fourty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) >= 30 and float(item.get_market_change_percent()) <= 40:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_below_zero_to_ten() is not None and self.__mFilterData.get_mover_below_zero_to_ten():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= 0 and float(item.get_market_change_percent()) >= -10:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_below_ten_to_twenty() is not None and self.__mFilterData.get_mover_below_ten_to_twenty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= -10 and float(item.get_market_change_percent()) >= -20:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_below_twenty_to_thirty() is not None and self.__mFilterData.get_mover_below_twenty_to_thirty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= -20 and float(item.get_market_change_percent()) >= -30:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_below_thirty_to_fourty() is not None and self.__mFilterData.get_mover_below_thirty_to_fourty():
                    if item.get_market_change_percent() and float(item.get_market_change_percent()) <= -30 and float(item.get_market_change_percent()) >= -40:
                        items.append(item)

                if self.__mFilterData.get_fifty_value_max_mover() is not None and self.__mFilterData.get_fifty_value_max_mover() and self.__mFilterData.get_fifty_value_min_mover() is not None and self.__mFilterData.get_fifty_value_min_mover():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) <= float(self.__mFilterData.get_fifty_value_max_mover()) and float(item.get_market_change_percent()) >= float(self.__mFilterData.get_fifty_value_min_mover()):
                        items.append(item)
                elif self.__mFilterData.get_fifty_value_max_mover() is not None and self.__mFilterData.get_fifty_value_max_mover():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) <= float(self.__mFilterData.get_fifty_value_max_mover()):
                        items.append(item)
                elif self.__mFilterData.get_fifty_value_min_mover() is not None and self.__mFilterData.get_fifty_value_min_mover():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) >= float(self.__mFilterData.get_fifty_value_min_mover()):
                        items.append(item)

                if self.__mFilterData.get_mover_fifty_weeks_above_zero() is not None and self.__mFilterData.get_mover_fifty_weeks_above_zero():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) >= 0:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_above_fifty() is not None and self.__mFilterData.get_mover_fifty_weeks_above_fifty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) >= 50:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_above_hundred() is not None and self.__mFilterData.get_mover_fifty_weeks_above_hundred():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) >= 100:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_below_zero() is not None and self.__mFilterData.get_mover_fifty_weeks_below_zero():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) < 0:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_below_fifty() is not None and self.__mFilterData.get_mover_fifty_weeks_below_fifty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) < 0:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_above_zero_to_ten() is not None and self.__mFilterData.get_mover_fifty_weeks_above_zero_to_ten():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) > 0 and float(item.get_fifty_two_weeks_perc_change()) <= 10:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_above_ten_to_twenty() is not None and self.__mFilterData.get_mover_fifty_weeks_above_ten_to_twenty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) > 10 and float(item.get_fifty_two_weeks_perc_change()) <= 20:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_above_twenty_to_thirty() is not None and self.__mFilterData.get_mover_fifty_weeks_above_twenty_to_thirty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) > 20 and float(item.get_fifty_two_weeks_perc_change()) <= 30:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_above_thirty_to_fourty() is not None and self.__mFilterData.get_mover_fifty_weeks_above_thirty_to_fourty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) > 30 and float(item.get_fifty_two_weeks_perc_change()) <= 40:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_below_zero_to_ten() is not None and self.__mFilterData.get_mover_fifty_weeks_below_zero_to_ten():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) < 0 and float(item.get_fifty_two_weeks_perc_change()) > -10:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_below_ten_to_twenty() is not None and self.__mFilterData.get_mover_fifty_weeks_below_ten_to_twenty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) < -10 and float(item.get_fifty_two_weeks_perc_change()) > -20:
                        items.append(item)
                        
                
                if self.__mFilterData.get_mover_fifty_weeks_below_twenty_to_thirty() is not None and self.__mFilterData.get_mover_fifty_weeks_below_twenty_to_thirty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) < -20 and float(item.get_fifty_two_weeks_perc_change()) > -30:
                        items.append(item)
                        

                if self.__mFilterData.get_mover_fifty_weeks_below_thirty_to_fourty() is not None and self.__mFilterData.get_mover_fifty_weeks_below_thirty_to_fourty():
                    if item.get_fifty_two_weeks_perc_change() and float(item.get_fifty_two_weeks_perc_change()) < -30 and float(item.get_fifty_two_weeks_perc_change()) > -40:
                        items.append(item)

            if len(items) > 0:
                self.__mFilteredItems = items
        else:
            self.__mFilteredItems = self.__mItems

    def unbind_listener(self):
        self.Unbind(wx.EVT_LIST_ITEM_SELECTED)

    def bind_listener(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
#endregion