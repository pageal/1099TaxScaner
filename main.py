# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import sys
import pandas

class transaction_scanner_firstrade_csv:
    def __init__(self):
        self.src_columns = [
            "Symbol"
            , "Quantity"
            , "Price"
            , "Action"
            , "Description"
            , "TradeDate"
            , "SettledDate"
            , "Interest"
            , "Amount"
            , "Commission"
            , "Fee"
            , "CUSIP"
            , "RecordType"]

        self.tgt_columns_1099 = [
            "Symbol"
            , "Description"
            , "Quantity"
            , "Date Acquired"
            , "Date Sold"
            , "Sales Proceeds"
            , "Cost"
            , "Total Gain / Loss "
            , "% Gain / Loss"]
        self.src_csv_path = ""
        self.dic_stocks_to_transaction = {}

    def import_csv(self, path):
        self.src_csv_path = path
        csv_data_frame = pandas.read_csv(path)
        for key, item in csv_data_frame.iterrows():
            if item["Symbol"] not in self.dic_stocks_to_transaction:
                self.dic_stocks_to_transaction[item["Symbol"]] = []
            self.dic_stocks_to_transaction[item["Symbol"]].append(item)

    def build_1099(self):
        self.all_tax_events = []
        for key, ticker_transactions in self.dic_stocks_to_transaction.items():
            ticker_buy_transactions = []
            for i in range(0, len(ticker_transactions)):
                transaction = ticker_transactions[i]
                if(transaction["Action"]=="BUY"):
                    ticker_buy_transactions.append(transaction)
                    #if transaction["Symbol"].strip() == "BND":
                    #    print(transaction.to_list())
                elif (transaction["Action"]=="SELL"):
                    #if transaction["Symbol"].strip() == "BND":
                    #    print(transaction.to_list())
                    tax_event_hdr = [transaction["Symbol"]]
                    tax_event_hdr = tax_event_hdr + [transaction["Description"]]
                    if(len(ticker_buy_transactions) == 0):
                        print(f"empty buy list for {transaction['Symbol']} at {transaction['TradeDate']}")
                    sales_proceeds = 0
                    to_sell = abs(int(float(transaction["Quantity"])))
                    to_pop = 0
                    for buy_event in ticker_buy_transactions:
                        if to_sell == 0:
                            break;
                        bought = float(buy_event["Quantity"])
                        if to_sell >= bought:
                            sell_amount = bought
                            to_sell -= bought
                            to_pop += 1
                        else:
                            sell_amount = to_sell
                            buy_event["Quantity"]=bought-sell_amount
                            to_sell = 0

                        tax_event = tax_event_hdr
                        tax_event = tax_event + [buy_event["Quantity"]]  # Quantity column
                        tax_event = tax_event + [buy_event["TradeDate"]]  # "Date Acquired" column
                        tax_event = tax_event + [transaction["TradeDate"]]  # "Date Sold" column
                        sales_sroceeds = int(sell_amount)*float(transaction["Price"])
                        tax_event = tax_event + [str(sales_sroceeds)]  # "Sales Proceeds" column
                        cost = int(sell_amount)*float(buy_event["Price"])
                        tax_event = tax_event + [str(cost)]  # "Sales Proceeds" column
                        tax_event = tax_event + [f"{sales_sroceeds-cost}"]  # "Total Gain / Loss" column

                        if(cost != 0):
                            prcnt = (sales_sroceeds-cost)/cost
                        else:
                            prcnt = 0
                        tax_event = tax_event + [f"{prcnt*100}"]  # "% Gain / Loss" column
                        self.all_tax_events.append(tax_event)
                    for i in range(0,to_pop):
                        ticker_buy_transactions.pop(0)
        tax_df = pandas.DataFrame(self.all_tax_events, columns=self.tgt_columns_1099)
        tax_df.to_csv("1099.csv")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ts = transaction_scanner_firstrade_csv()
    ts.import_csv("FT_CSV_63856457_2021_01_09.csv")
    ts.build_1099()
    print("done")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
