import pandas as pd
from customer_cohort import get_analyzed_date

def get_df_status_date_client(df, status_datetime_columnname, status_name):
    """
    Function to return a dataframe containing only client, status and date of status update
    @param df <pandas DataFrame>: dataframe from the customer_datasource.csv file
    @param status_datetime_columnname <string>: name of the column containing the date of the status
    @param status_name <string>: name of the status to be returned
    """

    # create a new dataframe containing only relevant columns and rows
    df_status = df[df[status_datetime_columnname].notnull()][["id", status_datetime_columnname]]

    # assign a new column named status, rename the datetime field to a common name (date) and convert to date
    df_status['status'] = status_name
    df_status.rename(columns={status_datetime_columnname: "date"}, inplace=True)
    df_status['date'] = pd.to_datetime(df_status.date)
    df_status['date'] = df_status['date'].dt.strftime('%Y-%m-%d')

    return df_status


def get_final_acquisition_dataframe(df):
    """
    Function to return a dataframe containing all status from all clients with respective dates
    This way Tableau handles better the data to display the acquisition funnel analysis.
    @param df <pandas DataFrame>: dataframe from the customer_datasource.csv file
    """
    # Get clients, status and dates for each status
    df_acct_reg  = get_df_status_date_client(df, "account_registration_dt", "Account registered")
    df_eml_conf  = get_df_status_date_client(df, "account_email_confirmation_dt", "Email confirmed")
    df_cli_reg   = get_df_status_date_client(df, "client_registration_dt", "Client registered")
    df_cli_anlz  = get_df_status_date_client(df, "client_analysis_dt", "Client analyzed (approved or denied)")
    df_cli_actv  = get_df_status_date_client(df, "client_initial_deposit_dt", "Initial deposit")

    # Union all datasets and return the dataframe
    objs=[
        df_acct_reg,
        df_eml_conf,
        df_cli_reg,
        df_cli_anlz,
        df_cli_actv
    ]
    df_client_status = pd.concat(objs=objs)

    return df_client_status


def create_customer_acquisition_funnel_file():
    """
    Function to output the information relate to acquisition funnel into a file
    """
    print("Creating new customer_datasource_acquisition_funnel.csv...")

    # reads information from the datasource file
    df = pd.read_csv('output/customer_datasource.csv')

    # create new column to store analyzed datetime
    df["client_analysis_dt"] = df.apply(
        lambda row: get_analyzed_date(row.client_approval_dt, row.client_denial_dt),
        axis=1
    )

    # get final dataframe to be imported to csv
    df_client_status = get_final_acquisition_dataframe(df)

    # Output result to a csv file
    df_client_status.to_csv('output/customer_datasource_acquisition_funnel.csv')

    print("New file customer_datasource_acquisition_funnel.csv done!")