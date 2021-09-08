import customer_registration
import customer_cohort
import customer_acquisition_funnel
import customer_transactions
import customer_activity

if __name__ == "__main__":

    ## PARAMETERS ##
    NUM_OF_CUSTOMERS = 10 # Number of customers to create
    MONTHS_BACK = 6 # Number of months back when customers create account

    # Create 1st file: customer_registration.csv
    customer_registration.create_customer_registration_file(NUM_OF_CUSTOMERS, MONTHS_BACK)

    # Create 2nd file: customer_datasource_cohort.csv
    customer_cohort.create_customer_cohort_file()

    # Create 3rd file: customer_datasource_acquisition_funnel.csv
    customer_acquisition_funnel.create_customer_acquisition_funnel_file()

    # Create 4th file: customer_transactions.csv
    customer_transactions.create_customer_transactions_file()

    # Create 5th file: customer_activity.csv
    customer_activity.create_customer_activity_file()