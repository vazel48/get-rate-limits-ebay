# get-rate-limits-eBay
Script for receiving and logging the number of API requests made.

This script logs records every 15 minutes to 15_minutes_log.csv and once a day the total number of requests per day to the daily_logs.csv.
It was launched according to the CRON task every 15 minutes.
The specificity is that eBay resets the limits approximately at UTC +8, although it is stated that at UTC +7.
