# -*- coding: utf-8 -*-
"""
Developed by Renato Rossi in 09/03/2021

This code creates 3 files with random users to be used
in a marketing dashboard.
"""

import pandas as pd
import numpy as np
from faker import Faker
from google.colab import drive
from datetime import datetime, date, timedelta

# Mount drive from Google Drive to input / output the information into a csv file
drive.mount('drive')

def create_new_random_user(account_id):
  fake = Faker(['en_US'])

  # New Account > Confirm email > New Client Info > Approve / Deny > Initial Deposit
  status = "Account registered"
  account_registration_dt = fake.date_time_between(start_date="-6M")
  account_email_confirmation_dt = None
  account_email_confirmation_dt_str = None
  client_registration_dt = None
  client_registration_dt_str = None
  client_approval_dt = None
  client_approval_dt_str = None
  client_denial_dt = None
  client_denial_dt_str = None
  client_initial_deposit_dt = None
  client_initial_deposit_dt_str = None

  # Randomly sets if client confirmed email
  if fake.boolean():
    account_email_confirmation_dt = fake.date_time_between_dates(
        datetime_start = account_registration_dt
    )
    account_email_confirmation_dt_str = account_email_confirmation_dt.strftime('%Y-%m-%d %H:%M:%S')
    status = "Email confirmed"

  # Randomly sets if client finished registration
  if account_email_confirmation_dt is not None and fake.boolean():
    client_registration_dt = fake.date_time_between_dates(
        datetime_start = account_email_confirmation_dt
    )
    client_registration_dt_str = client_registration_dt.strftime('%Y-%m-%d %H:%M:%S')
    status = "Client registered"

  # Randomly sets if client was approved
  if client_registration_dt is not None and fake.boolean():
    client_approval_dt = fake.date_time_between_dates(
        datetime_start = client_registration_dt
    )
    client_approval_dt_str = client_approval_dt.strftime('%Y-%m-%d %H:%M:%S')
    status = "Client approved"

  # Randomly sets if client was denied
  if client_registration_dt is not None and client_approval_dt is not None and fake.boolean():
    client_denial_dt = fake.date_time_between_dates(
        datetime_start = client_registration_dt
    )
    client_denial_dt_str = client_denial_dt.strftime('%Y-%m-%d %H:%M:%S')
    status = "Client denied"

  # Randomly sets initial deposit (only for approved clients)
  if client_approval_dt is not None and fake.boolean():
    client_initial_deposit_dt = fake.date_time_between_dates(
        datetime_start = client_approval_dt
    )
    client_initial_deposit_dt_str = client_initial_deposit_dt.strftime('%Y-%m-%d %H:%M:%S')
    status = "Client denied"
  client_initial_deposit_dt

  user = {
      'id': account_id,
      'name': fake.unique.name(),
      'address': fake.address(),
      'birthdate': fake.date_this_century().strftime('%Y-%m-%d'),
      'status': status,
      'account_registration_dt': account_registration_dt.strftime('%Y-%m-%d %H:%M:%S'),
      'account_email_confirmation_dt': account_email_confirmation_dt_str,
      'client_registration_dt': client_registration_dt_str,
      'client_approval_dt': client_approval_dt_str,
      'client_denial_dt': client_denial_dt_str,
      'client_initial_deposit_dt': client_initial_deposit_dt_str,
  }

  return user

def create_cohort_datasource_file():
  users_list = []
  for i in range(15293):
    users_list.append(create_new_random_user(i))

  columns=[
    'id',
    'name',
    'address',
    'birthdate',
    'status',
    'account_registration_dt',
    'account_email_confirmation_dt',
    'client_registration_dt',
    'client_approval_dt',
    'client_denial_dt',
    'client_initial_deposit_dt',         
  ]
  df = pd.DataFrame(users_list, columns=columns)
  
  # Output result to a csv file and copy it to Google Drive
  df.to_csv('customer_datasource.csv')

# Copy file to final location
create_cohort_datasource_file()
!cp customer_datasource.csv "drive/My Drive/Colab Notebooks/Tableau Portfolio"

"""Put cohort_datasource.csv file into a better formatting for Tableau"""

def days_between_dates(date1, date2):
  """
  Function to calculate the difference in days between two dates
  @param date1: first date (latest)
  @param date2: second date (oldest)
  """
  if date1 is not None and date2 is not None:
    date1 = datetime.strptime(date1, "%Y-%m-%d")
    date2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((date2 - date1).days)
  else:
    return None


def get_analyzed_date(dt1, dt2):
  """
  Function to get analyzed datetime (get first non null date)
  @param d1: approved datetime
  @param d2: denied datetime
  """
  if dt1 is not None or dt2 is not None:
    if dt1 is not None:
      return dt1
    else:
      return dt2
  else:
    return None

# read the file containing all client information
df = pd.read_csv('customer_datasource.csv')

# create new column to store analyzed datetime
df["client_analysis_dt"] = df.apply(
    lambda row: get_analyzed_date(row.client_approval_dt, row.client_denial_dt),
    axis=1
)

def get_df_client_count(df, columnname_date_from, columnname_date_to, status_from, status_to):
  # filter only relevant values based on date
  df_client_count = df[df[columnname_date_from].notnull()][["id", columnname_date_from, columnname_date_to]]
  
  # rename date columns
  columns_rename = {
    columnname_date_from : 'status_datetime_from', 
    columnname_date_to : 'status_datetime_to'
  }
  df_client_count.rename(columns=columns_rename, inplace=True)

  # add numbers to count customers in the end
  df_client_count['status_from_count'] = 1
  df_client_count['status_to_count'] = np.where(df_client_count.status_datetime_to.notnull(), 1, 0)

  # transform columns from datetime to date
  df_client_count['status_datetime_from'] = pd.to_datetime(df_client_count.status_datetime_from)
  df_client_count['status_datetime_from'] = df_client_count['status_datetime_from'].dt.strftime('%Y-%m-%d')
  df_client_count['status_datetime_to'] = pd.to_datetime(df_client_count.status_datetime_to)
  df_client_count['status_datetime_to'] = df_client_count['status_datetime_to'].dt.strftime('%Y-%m-%d')

  # count clients: first calculate whole population from, then get conversions and in the end merge both info
  df_client_count_status_from = df_client_count.groupby(["status_datetime_from"]).sum().reset_index()[["status_datetime_from", "status_from_count"]]
  df_client_count_status_to = df_client_count.groupby(["status_datetime_from", "status_datetime_to"]).sum().reset_index()[["status_datetime_from", "status_datetime_to", "status_to_count"]]
  df_client_count = pd.merge(df_client_count_status_to, df_client_count_status_from, how="left", on=["status_datetime_from"])

  # create status columns
  df_client_count['status_from'] = status_from
  df_client_count['status_to'] = status_to
    
  return df_client_count

##          ##
## STATUSES ##
##          ##
statuses = {
    "order": [1, 2, 3, 4, 5],
    "status": [
      'Account registered',
      'Email confirmed',
      'Client registered',
      'Client analyzed (approved or denied)',
      'Initial deposit'      
    ]
}

# Creates 2 different dataframes from the statuses
df_status_list1 = pd.DataFrame(statuses)
df_status_list1['id'] = 1
df_status_list2 = pd.DataFrame(statuses)
df_status_list2['id'] = 1

# Create a final dataframe with all possible combinations
df_statuses_final = pd.merge(df_status_list1, df_status_list2, on="id", how="outer")
df_statuses_final = df_statuses_final[df_statuses_final["order_x"] < df_statuses_final["order_y"]][["status_x", "status_y"]]

# Create a new field to do all possible combinations with date
df_statuses_final['id'] = 1

##       ##
## DATES ##
##       ##

# Create all days from min date to today
min_registration_date = datetime.strptime(df["account_registration_dt"].min(), '%Y-%m-%d %H:%M:%S')
start_date = min_registration_date.date()
end_date = date.today()
delta = end_date - start_date
dates_list = []
for i in range(delta.days + 1):
    date = start_date + timedelta(days=i)
    dates_list.append(date.strftime('%Y-%m-%d'))

df_dates = pd.DataFrame(data=dates_list, columns=['date'])

# Do all possible combinations
df_dates_list1 = pd.DataFrame(df_dates)
df_dates_list1['id'] = 1
df_dates_list2 = pd.DataFrame(df_dates)
df_dates_list2['id'] = 1

# Use just relevant data (feasible dates)
df_dates_final = pd.merge(df_dates_list1, df_dates_list2, on="id", how="outer")
df_dates_final = df_dates_final[df_dates_final["date_x"] <= df_dates_final["date_y"]][["date_x", "date_y"]]

# Calculate date difference in days
df_dates_final['datetime_diff_days'] = df_dates_final.apply(
  lambda row: days_between_dates(row.date_x, row.date_y), 
  axis=1
)

# Create a new field to do all possible combinations with statuses
df_dates_final['id'] = 1

##               ##
## CLIENT COUNTS ##
##               ##
df_case1_2 = get_df_client_count(df, "account_registration_dt", "account_email_confirmation_dt", "Account registered", "Email confirmed")
df_case1_3 = get_df_client_count(df, "account_registration_dt", "account_email_confirmation_dt", "Account registered", "Client registered")
df_case1_4 = get_df_client_count(df, "account_registration_dt", "account_email_confirmation_dt", "Account registered", "Client analyzed (approved or denied)")
df_case1_5 = get_df_client_count(df, "account_registration_dt", "account_email_confirmation_dt", "Account registered", "Initial deposit")

df_case2_3 = get_df_client_count(df, "account_email_confirmation_dt", "client_registration_dt", "Email confirmed", "Client registered")
df_case2_4 = get_df_client_count(df, "account_email_confirmation_dt", "client_registration_dt", "Email confirmed", "Client analyzed (approved or denied)")
df_case2_5 = get_df_client_count(df, "account_email_confirmation_dt", "client_registration_dt", "Email confirmed", "Initial deposit")

df_case3_4 = get_df_client_count(df, "client_registration_dt", "client_analysis_dt", "Client registered", "Client analyzed (approved or denied)")
df_case3_5 = get_df_client_count(df, "client_registration_dt", "client_analysis_dt", "Client registered", "Initial deposit")

df_case4_5 = get_df_client_count(df, "client_initial_deposit_dt", "client_analysis_dt", "Client analyzed (approved or denied)", "Initial deposit")

# Union all dataframes
objs=[
  df_case1_2, df_case1_3, df_case1_4, df_case1_5,
  df_case2_3, df_case2_4, df_case2_5,
  df_case3_4, df_case3_5,
  df_case4_5
]
df_client_counts = pd.concat(objs=objs)

##                                          ##
## ALL COMBINATIONS BETWEEN DATE AND STATUS ##
##                                          ##
# Create a dataframe with all combinations of dates and statuses
df_final_cohort = pd.merge(df_dates_final, df_statuses_final, on="id", how="outer")

# Rename columns for the join with client counts and drop unused field (id)
columns_rename = {
    'date_x': 'status_datetime_from',
    'date_y': 'status_datetime_to',
    'status_x': 'status_from',
    'status_y': 'status_to',
}
df_final_cohort.rename(columns=columns_rename, inplace=True)
df_final_cohort.drop(columns=['id'], inplace=True)

# Join information from all dates and statuses with client counts
df_final_cohort = df_final_cohort.merge(
  df_client_counts, 
  on=["status_datetime_from", "status_datetime_to", "status_from", "status_to"], 
  how="left"
)
# Replace non matching rows with 0 on the count
df_final_cohort['status_from_count'] = df_final_cohort['status_from_count'].fillna(0)
df_final_cohort['status_from_count'] = df_final_cohort['status_from_count'].astype('Int64')
df_final_cohort['status_to_count'] = df_final_cohort['status_to_count'].fillna(0)
df_final_cohort['status_to_count'] = df_final_cohort['status_to_count'].astype('Int64')

# Output result to a csv file and copy it to Google Drive
df_final_cohort.to_csv('customer_datasource_cohort.csv')
!cp customer_datasource_cohort.csv "drive/My Drive/Colab Notebooks/Tableau Portfolio"

"""#Acquisition Funnel File"""

df = pd.read_csv('customer_datasource.csv')

# create new column to store analyzed datetime
df["client_analysis_dt"] = df.apply(
    lambda row: get_analyzed_date(row.client_approval_dt, row.client_denial_dt),
    axis=1
)

df.columns

def get_df_status_date_client(df, status_datetime_columnname, status_name):
  df_status = df[df[status_datetime_columnname].notnull()][["id", status_datetime_columnname]]
  df_status['status'] = status_name
  df_status.rename(columns={status_datetime_columnname: "date"}, inplace=True)
  df_status['date'] = pd.to_datetime(df_status.date)
  df_status['date'] = df_status['date'].dt.strftime('%Y-%m-%d')
  return df_status

df_acct_reg  = get_df_status_date_client(df, "account_registration_dt", "Account registered")
df_eml_conf  = get_df_status_date_client(df, "account_email_confirmation_dt", "Email confirmed")
df_cli_reg   = get_df_status_date_client(df, "client_registration_dt", "Client registered")
df_cli_anlz  = get_df_status_date_client(df, "client_analysis_dt", "Client analyzed (approved or denied)")
df_cli_actv  = get_df_status_date_client(df, "client_initial_deposit_dt", "Initial deposit")

objs=[df_acct_reg,df_eml_conf,df_cli_reg,df_cli_anlz,df_cli_actv]
df_client_status = pd.concat(objs=objs)

# Output result to a csv file and copy it to Google Drive
df_client_status.to_csv('customer_acquisition_funnel.csv')
!cp customer_acquisition_funnel.csv "drive/My Drive/Colab Notebooks/Tableau Portfolio"