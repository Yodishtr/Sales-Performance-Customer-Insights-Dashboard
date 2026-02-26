import pandas as pd


def checkForDuplicates(dataframe):
    duplicate_rows_subset = dataframe.duplicated(keep=False)
    
    if (duplicate_rows_subset.any()):
        dataframe = dataframe.drop_duplicates(keep="first")
    return dataframe
    
        
    
def checkForNulls(dataframe):
    list_of_important_cols = ["order_date", "ship_date", "sales", "profit", "quantity", "order_id", "product_id"]
    number_of_nulls = dataframe[list_of_important_cols].isna().sum()
    if (number_of_nulls.sum() > 0):
        dataframe = dataframe.dropna(subset=list_of_important_cols)
    return dataframe

def standardiseColumnNames(dataframe):
    dataframe.columns = (dataframe.columns.str.strip().str.replace(r"\s+", "_", regex=True).str.lower())
    return dataframe

def removeIllegalValues(dataframe):
    incorrect_sales = dataframe[dataframe["sales"] < 0]
    incorrect_quantity = dataframe[dataframe["quantity"] < 0]
    incorrect_shipping_date = dataframe[dataframe["ship_date"] < dataframe["order_date"]]
    if (incorrect_sales.shape[0] > 0):
        dataframe = dataframe[dataframe["sales"] >= 0]
    if (incorrect_quantity.shape[0] > 0):
        dataframe = dataframe[dataframe["quantity"] >= 0]
    if (incorrect_shipping_date.shape[0] > 0):
        dataframe = dataframe[dataframe["ship_date"] >= dataframe["order_date"]]
    return dataframe


if __name__ == "__main__":
    data_frame = pd.read_csv("raw_data/Superstore.csv", encoding="cp1252")
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"], format='%m/%d/%Y', errors="coerce")
    data_frame["Ship Date"] = pd.to_datetime(data_frame["Ship Date"], format='%m/%d/%Y', errors="coerce")
    data_frame = standardiseColumnNames(data_frame)
    data_frame = checkForDuplicates(data_frame)
    data_frame = checkForNulls(data_frame)
    data_frame = removeIllegalValues(data_frame)

    # profit margin col:
    data_frame["profit_margin"] = (data_frame["profit"] / data_frame["sales"]) * 100
    # aggregate some time using year and month
    data_frame["order_year"] = data_frame["order_date"].dt.year
    data_frame["order_month"] = data_frame["order_date"].dt.month
    # y-m for charts later on
    data_frame["year_month"] = data_frame["order_date"].dt.strftime("%Y-%m")
    # total income per customer
    total_inc_cus = data_frame.groupby("customer_id")["sales"].sum().reset_index()
    total_inc_cus.columns = ["customer_id", "customer_tr"]
    data_frame = data_frame.merge(total_inc_cus, on="customer_id")
    # distinguish customer from high spender vs low spender
    current_median = data_frame["customer_tr"].median()
    data_frame["spender_type"] = data_frame["customer_tr"].apply(
        lambda x: "High Spender" if x >= current_median else "Low Spender"
    )
    # number of sales per unti
    data_frame["sales_per_unit"] = data_frame["sales"] / data_frame["quantity"]

    data_frame.to_csv("cleaned_output/cleaned_data.csv", index=False)