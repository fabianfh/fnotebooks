import QuantLib as ql
from ReadExcel import *
from openpyxl import *
import re
import pandas as pd

def printDatum(data,digits=2):
    format = '%%.%df %%%%' % digits
    return  "Maturity: " + str(ql.Period(data.numTimeUnits,data.timeUnit))+ "\tQuoted Rate:"+format % (100*data.rate)

def printOISwapDatum(data,digits=2):
    format = '%%.%df %%%%' % digits
    return  "Maturity: " + str(ql.Period(data.numTimeUnits,data.timeUnit))+ "\tQuoted Rate:"+format % (100*data.rate)

def printLIBORSwapDatum(data,digits=2):
    format = '%%.%df %%%%' % digits
    return  "Maturity: " + str(ql.Period(data.numTermUnits,data.termUnit))
    + "\t(Index:"  + str(ql.Period(data.numIndexUnits,data.indexUnit)) + ")"
    + "\tQuoted Rate:"+format % (100*data.rate)

def formatPrice(p,digits=2):
    format = '%%.%df' % digits
    return format % p

def formatRate(r,digits=2):
    format = '%%.%df %%%%' % digits
    return format % (r*100)

def formatVol(v, digits = 2):
    format = '%%.%df %%%%' % digits
    return format % (v * 100)

def formatPrice(p, digits = 2):
    format = '%%.%df' % digits
    return format % p

class MarketConventions(object):
    def __init__(self):
        self.settlementDays = 2
        self.calendar = ql.TARGET()
        self.fixedEoniaConvention = ql.ModifiedFollowing
        self.floatingEoniaConvention = ql.ModifiedFollowing
        self.fixedEoniaPeriod = 1 * ql.Years
        self.floatingEoniaPeriod = 1 * ql.Years
        self.fixedEoniaDayCount = ql.Actual360()
        self.floatingEoniaDayCount = ql.Actual360()
        self.fixedSwapConvention = ql.ModifiedFollowing
        self.fixedSwapFrequency = ql.Annual
        self.fixedSwapDayCount = ql.Thirty360(ql.Thirty360.BondBasis)
        self.floatSwapConvention = ql.ModifiedFollowing
        self.floatSwapFrequency = ql.Semiannual
        self.floatSwapDayCount = ql.Actual360()




class Datum(object):
    """Whatever."""
    def __init__(self, numSettlementDays,timeUnit,numTimeUnits,rate):
        """Arguments:"""
        """numSettlementDays:\tNumber of days between inception and accrue start"""
        """timeUnit:\tTime unit ofthe accrue periods length"""
        """numTimeUnits:\tNumber of time units in the accrue period"""
        """rate:\tThe Coupon"""
        self.numSettlementDays = numSettlementDays
        self.timeUnit = timeUnit
        self.numTimeUnits = numTimeUnits
        self.rate = rate
    def __repr__(self):
        """Returns a string representation of this object that can
        be evaluated as a Python expression."""
        return printDatum(self,4)
    __str__ = __repr__
    """The str and repr forms of this object are the same."""




class SwapDatum(object):
    """Fra Quote along with instrument data."""
    def __init__(self,settlementDays,indexUnit,numIndexUnits,termUnit,numTermUnits,rate):
        self.settlementDays = settlementDays
        self.indexUnit = indexUnit
        self.numIndexUnits = numIndexUnits
        self.termUnit = termUnit
        self.numTermUnits = numTermUnits
        self.rate = rate

    def __repr__(self):
        """Returns a string representation of this object that can
        be evaluated as a Python expression."""
        return   printOISwapDatum(self,4)

    __str__ = __repr__
    """The str and repr forms of this object are the same."""



class MarketData(object):
    def __init__(self,depoQuotes,oiSwapQuotes,swapQuotes):
        self.depoQuotes = depoQuotes
        self.swapQuotes = swapQuotes
        self.oiSwapQuotes = oiSwapQuotes
        #self.oiSwapQuotesDF = self.makeDataFrame(self.oiSwapQuotes)
        #self.swapQuotesDF = self.makeDataFrame(self.swapQuotes)
        #self.depoQuotesDF = self.makeDataFrame(self.depoQuotes)

def makeDataFrame(quotes):
         maturity = pd.Series([ql.Period(quote.numTimeUnits,quote.timeUnit) for quote in quotes], name='Maturity')
         rate = pd.Series([quote.rate for quote in quotes], name='Rate')
         retval = pd.DataFrame({maturity.name : maturity, rate.name : rate})
         return retval

def get_year_frac(today,periods,bDayConvention):
            return [ql.Actual360().yearFraction(today,maturity)
             for maturity in [ ql.TARGET().adjust(today + period, bDayConvention)
             for period in periods]]

def map_RTRtenor_to_quantlib_period(tenor):
    return map_RTRtenor_to_qlPeriod[tenor]

map_RTRtenor_to_qlPeriod = {
    "ON":ql.Period(1,ql.Days),
    "TN":ql.Period(1,ql.Days),
    "SN":ql.Period(1,ql.Days),
    "SW":ql.Period(1,ql.Weeks),
    "2W":ql.Period(2,ql.Weeks),
    "3W":ql.Period(3,ql.Weeks),
    "1M":ql.Period(1,ql.Months),
    "2M":ql.Period(2,ql.Months),
    "3M":ql.Period(3,ql.Months),
    "4M":ql.Period(4,ql.Months),
    "5M":ql.Period(5,ql.Months),
    "6M":ql.Period(6,ql.Months),
    "7M":ql.Period(7,ql.Months),
    "8M":ql.Period(8,ql.Months),
    "9M":ql.Period(9,ql.Months),
    "10M":ql.Period(10,ql.Months),
    "11M":ql.Period(11,ql.Months),
    "1Y":ql.Period(1,ql.Years),
    "15M":ql.Period(15,ql.Months),
    "18M":ql.Period(18,ql.Months),
    "21M":ql.Period(21,ql.Months),
    "2Y":ql.Period(2,ql.Years),
    "3Y":ql.Period(3,ql.Years),
    "4Y":ql.Period(4,ql.Years),
    "5Y":ql.Period(5,ql.Years),
    "6Y":ql.Period(6,ql.Years),
    "7Y":ql.Period(7,ql.Years),
    "8Y":ql.Period(8,ql.Years),
    "9Y":ql.Period(9,ql.Years),
    "10Y":ql.Period(10,ql.Years),
    "11Y":ql.Period(11,ql.Years),
    "12Y":ql.Period(12,ql.Years),
    "15Y":ql.Period(15,ql.Years),
    "20Y":ql.Period(20,ql.Years),
    "25Y":ql.Period(25,ql.Years),
    "30Y":ql.Period(30,ql.Years)
    }



def map_BBtenor_to_quantlib(tenor):
    if tenor == "YR":
        return ql.Years
    elif tenor == "MO":
        return ql.Months
    elif tenor == "WK":
        return ql.Weeks
    elif tenor == "DY":
        return ql.Days
    else:
        raise Exception("Faild to map tenor:" + str(tenor))

def getMarketData(path, ws_name, col_names):
    wb = load_workbook(path)
    ws = wb.get_sheet_by_name(ws_name)
    list = get_list_from_cols(col_names,ws)


    depoQuotes = []
    oiSwapQuotes = []
    SwapQuotes = []

    for item in list:
        if ( ('InstType' in item) & (item['InstType'] == 'CASH')):
            numSettlementDays = 0
            matchResult = re.match("([0-9]{1,2}) ([a-zA-Z][a-zA-Z])", item['Term'], flags=0)
            if(matchResult):
                timeUnit = map_BBtenor_to_quantlib(matchResult.group(2))
                numTimeUnits = int(matchResult.group(1))
                rate = item['Mid']
                timeUnit = map_BBtenor_to_quantlib(matchResult.group(2))
                numTimeUnits = int(matchResult.group(1))
                rate = item['Mid']
                depoQuotes.append(Datum(numSettlementDays,timeUnit,numTimeUnits,rate/100))
            else:
                print("Could not parse " + item['InstType'] + ' ' + 'Term' + ": " +item['Term'] )
        elif(('InstType' in item) & (item['InstType'] == 'SWAP' )
             & ('InstDes' in item)  & ( 'EONIA' in item['InstDes'])):
            numSettlementDays = 2
            matchResult = re.match("([0-9]{1,2}) ([a-zA-Z][a-zA-Z])", item['Term'], flags=0)
            if(matchResult):
                timeUnit = map_BBtenor_to_quantlib(matchResult.group(2))
                numTimeUnits = int(matchResult.group(1))
                rate = item['Mid']
                oiSwapQuotes.append(Datum(numSettlementDays,timeUnit,numTimeUnits,rate/100))
        else:
            print("Could not parse " + item['InstType'] + ' ' + 'Term' + ": " +item['Term'] )

    return MarketData(depoQuotes,oiSwapQuotes,SwapQuotes)

