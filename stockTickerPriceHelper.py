import urllib2
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta

# static helper class to help with getting and parsing
# closing prices for a given ticker for some date range.
# Uses Yahoo finance apis.
ONE_DAY = timedelta(days=1);
class InvestmentHelper(object):

	# The given date is the csv data returned from YAHOO finance. The
	# first column will be the date as YYYY-MM-DD. There needs to be a
	# single column named "Close" with the close price.
	# This method creates a dictionary of date to closing price for every date.
	# For weekends/holidays/etc, this will fill in the data in the map using
	# the previous day's closing price. Assumes data in the csv is sorted by
	# date with newest data first and the oldest data last.
	@staticmethod
	def mapDateToClosePrice(csvData):

		# find the column index for the closing price
		header = csvData[0];
		cols = header.split(",");
		index = 0;
		closeIndex = -1;
		for colName in cols:
			if (colName == "Close"):
				closeIndex = index;
				break;
			index = index + 1;
		isFirstLine = True;

		# keep track of previous date as need to fill in data for weekends, etc
		prevDate = None;
		dateToPrice = {};
		for line in csvData:
			# ignore header
			if isFirstLine:
				isFirstLine = False;
				continue;
			rowColData = line.split(",");
			dateStr = rowColData[0];
			closePriceStr = rowColData[closeIndex];

			priceDateTime = datetime.strptime(dateStr, "%Y-%m-%d");
			priceDate = priceDateTime.date();

			dateToPrice[priceDate] = closePriceStr;

			# fill in missing dates
			if (not (prevDate is None)) :
				dateDiff = prevDate - priceDate;
				dayDiff = dateDiff.days;
				i = 1;
				currDate = priceDate;
				for i in range(1, dayDiff):
					currDate = currDate + ONE_DAY;
					dateToPrice[currDate] = closePriceStr;
			prevDate = priceDate;
		return dateToPrice;
	# function to get all the historical data for the given stock ticker
	# starting with the given date up to the present day.
	# month should be 1-12
	@staticmethod
	def getCSVPriceData(startMonth, startYear, startDay, ticker):
	  startDate = date(year=startYear, month=startMonth, day=startDay);
	  # start early so that we can fill in incase startDay is a weekend, etc
	  startDate = startDate + timedelta(days=-5);
	  month = startDate.month - 1;
	  yFinanceUrl = "http://ichart.finance.yahoo.com/table.csv?s=" \
	  + ticker + "&a=" + str(month) \
	  + "&b=" + str(startDate.day)  \
	  + "&c=" + str(startDate.year);
	  response = urllib2.urlopen(yFinanceUrl);
	
	  lines = response.readlines();
	  return lines;
