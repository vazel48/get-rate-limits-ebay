import requests
from datetime import datetime, timezone, timedelta
import os


def get_access_token(url):
    headers = {
        'User-Agent': "I'm fucking useless header, so as not to get 403 Forbidden"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}")


def get_rate_limit_data(api_url, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get rate limit data. Status code: {response.status_code}")


def calculate_used_limits(rate_limit_data, resource_name):
    for context in rate_limit_data['rateLimits']:
        for resource in context['resources']:
            if resource['name'] == resource_name:
                # Assuming only one rate per resource for simplicity
                rate_info = resource['rates'][0]
                return rate_info['limit'] - rate_info['remaining']
    return None  # If the resource name is not found, return None


token_url = "https://your-company.com/ebayaccesstoken.txt"
rate_limit_url = "https://api.ebay.com/developer/analytics/v1_beta/rate_limit/"

access_token = get_access_token(token_url)

rate_limit_data = get_rate_limit_data(rate_limit_url, access_token)

# Calculate used limits
used_getitem = calculate_used_limits(rate_limit_data, "GetItem")
used_buy_browse = calculate_used_limits(rate_limit_data, "buy.browse")
used_buy_browse_bulk = calculate_used_limits(rate_limit_data, "buy.browse.item.bulk")

current_dt_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Path for the result CSV file
csv_file_path = "/home/ubuntu/request-limits-logs/15_minutes_log.csv"

# Writing to CSV
with open(csv_file_path, 'a') as file:
    file.write(f"{current_dt_utc},{used_getitem},{used_buy_browse},{used_buy_browse_bulk}\n")

print(f"{current_dt_utc} Data written to {csv_file_path}")


""" Next, a block of code for extracting data and saving it in daily_logs """

daily_log_file_path = "/home/ubuntu/request-limits-logs/daily_logs.csv"
current_utc_datetime = datetime.now(timezone.utc)


def update_daily_log():
    # Determining the search date depending on the current time
    if current_utc_datetime.hour > 8:
        search_date = current_utc_datetime.date()
    else:
        search_date = (current_utc_datetime - timedelta(days=1)).date()

    # Checking if there is a record for the previous day in daily_logs.csv
    if os.path.exists(daily_log_file_path):
        with open(daily_log_file_path, 'r') as daily_log_file:
            if any(search_date.strftime('%Y-%m-%d') in line for line in daily_log_file):
                print(f"{current_dt_utc} Record for the previous day in daily_log file already exists.")
                return

    # Search for the last entry for the previous day before 8:00
    last_entry = None
    last_entry_date = None
    with open('/home/ubuntu/request-limits-logs/15_minutes_log.csv', 'r') as log_file:
        for line in log_file:
            line_date_str, _ = line.split(',', 1)  # Getting date and time from a string
            line_date = datetime.strptime(line_date_str, '%Y-%m-%d %H:%M:%S')
            if line_date.date() == search_date and line_date.hour < 8:
                last_entry = line
                last_entry_date = line_date.date()

    # Adding an entry to daily_logs.csv if found
    if last_entry and last_entry_date == search_date:
        with open(daily_log_file_path, 'a') as daily_log_file:
            daily_log_file.write(last_entry)
            print(f"{current_dt_utc} Data written to {daily_log_file_path}")
    else:
        print(f"{current_dt_utc} Records for previous day not found in 15_minutes_log.csv")


# Get the current time in UTC and set the range when the code should be executed
# Let's say we want to search and write from 08:01 to 08:20 UTC
start_time_utc = current_utc_datetime.replace(hour=8, minute=1, second=0)
end_time_utc = current_utc_datetime.replace(hour=8, minute=20, second=0)

# Execute the update_daily_log in the specified range
if start_time_utc <= current_utc_datetime <= end_time_utc:
    update_daily_log()
else:
    print(f"{current_dt_utc} Inappropriate time to execute update_daily_log")
