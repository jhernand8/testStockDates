import webapp2
import cgi 
import os
import urllib
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
from stockTickerPriceHelper import InvestmentHelper

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'])

class InvestDate(webapp2.RequestHandler):
  def post(self):
    monthStr = cgi.escape(self.request.get("month"));
    yearStr = cgi.escape(self.request.get("year"));
    amountStr = cgi.escape(self.request.get("amount"));
    tickersStr = cgi.escape(self.request.get("tickers"));
    month = int(monthStr);
    year = int(yearStr);
    amount = int(amountStr);

    tickersList = tickersStr.split(",");
    tickerToDatepriceMap = {};
    tickerToMaxDay = {};
    tickerToMinDay = {};
    tickerToAvg = {};
    for ticker in tickersList:
      data = InvestmentHelper.getCSVPriceData(month, year, 1, ticker);
      dateToPrice = InvestmentHelper.mapDateToClosePrice(data);
      count = 0;
      dayOfMToShares = self.processDataToMapOfDayOfMonthToShares(month, year, amount, dateToPrice);
      tickerToDatepriceMap[ticker] = dayOfMToShares;
      minDay = self.getKeyWithMinValue(dayOfMToShares);
      maxDay = self.getKeyWithMaxValue(dayOfMToShares);
      tickerToMinDay[ticker] = minDay;
      tickerToMaxDay[ticker] = maxDay;
      tickerToAvg[ticker] = self.getAvg(dayOfMToShares);

    template_values = {
      "amount": amount,
      "tickers": tickersList,
      "month": month,
      "year": year,
      "tickerToDayPrice": tickerToDatepriceMap,
      "tickerToMinDay": tickerToMinDay,
      "tickerToMaxDay": tickerToMaxDay,
      "tickerToAvg": tickerToAvg,
	    }
    
    template = JINJA_ENVIRONMENT.get_template("static/templates/dateTables.html")
    
    self.response.write(template.render(template_values))

  # Returns the average value of all the entries in the map.
  def getAvg(self, daySharesMap):
    sum = 0.0;
    count = 0;
    for key in daySharesMap:
      sum = sum + daySharesMap[key];
      count = count + 1;
    return sum / (float(count));
  # returns a map with keys 1-31. For each day 1-31 for every month, adds up
  # number of shares if bought amountPerInvestWorth of the stock on that day
  # of the month.
  def processDataToMapOfDayOfMonthToShares(self, startMonth, startYear, amountPerInvest, dateToPrice):

    startdate = date(year=startYear,day=1,month=startMonth);
    today = date.today();
    endDate = date(year=today.year, day=1,month=today.month);
    totalDayDiff = endDate - startdate;

    # map of day of a month to shares if bought on that day
    dayOfMonthToShares = {};
    for d in range(1, 32):
      dayOfMonthToShares[d] = 0.0;

    # go thru each day and compute number of shares that would have been
    # bought that day with amountPerInvest. If month has < 31 days, use the last
    # day of the month's data to fill in up to 31
    ONE_DAY = timedelta(days=1);
    currDate = startdate;
    for dayOffset in range(totalDayDiff.days):
	sharePrice = dateToPrice[currDate];
	shares = amountPerInvest / float(sharePrice);
	currDay = currDate.day;
	dayOfMonthToShares[currDay] = dayOfMonthToShares[currDay] + shares;
	currDate = currDate + ONE_DAY;

	# if start of the next day, then fill in for missing days ie 
	# up to 31
	nextDay = currDate.day;
	if (nextDay == 1):
		for day in range(currDay + 1, 32):
			dayOfMonthToShares[day] = dayOfMonthToShares[day] + shares;
    return dayOfMonthToShares;

  # Returns the key which maps to the minimum value in the map.
  def getKeyWithMinValue(self, dayToShares):
    minKey = None;
    minVal = None;
    for key in dayToShares:
      if (minKey == None or minVal > dayToShares[key]):
        minKey = key;
        minVal = dayToShares[key];
    return minKey;
  
  # Returns the key which maps to the maximum value in the map.
  def getKeyWithMaxValue(self, dayToShares):
    maxKey = None;
    maxVal = None;
    for key in dayToShares:
      if (maxKey == None or maxVal < dayToShares[key]):
        maxKey = key;
        maxVal = dayToShares[key];
    return maxKey;


application = webapp2.WSGIApplication([('/input', InvestDate),], debug=True)


