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
        self.oiSwapQuotesDF = self.makeDataFrame(self.oiSwapQuotes)   
        self.swapQuotesDF = self.makeDataFrame(self.swapQuotes)     
        self.depoQuotesDF = self.makeDataFrame(self.depoQuotes)     
        
    def makeDataFrame(self,quotes):
         maturity = pd.Series([ql.Period(quote.numTimeUnits,quote.timeUnit) for quote in quotes], name='Maturity')
         rate = pd.Series([quote.rate for quote in quotes], name='Rate')
         retval = pd.DataFrame({maturity.name : maturity, rate.name : rate})
         return retval

def get_year_frac(today,periods,bDayConvention):
            return [ql.Actual360().yearFraction(today,maturity) 
             for maturity in [ ql.TARGET().adjust(today + period, bDayConvention) 
             for period in periods]]

def getQuantLibMarketData():
    depoQuotes =  [
	#[ 0, 1, ql.Days, 1.10/100 ],
	[ 1, 1, ql.Days, 1.10/100 ],
	[ 2, 1, ql.Weeks, 1.40/100 ],
	[ 2, 2, ql.Weeks, 1.50/100 ],
	[ 2, 1, ql.Months, 1.70/100 ],
	[ 2, 2, ql.Months, 1.90/100 ],
	[ 2, 3, ql.Months, 2.05/100 ],
	[ 2, 4, ql.Months, 2.08/100 ],
	[ 2, 5, ql.Months, 2.11/100 ],
	[ 2, 6, ql.Months, 2.13/100 ]]

    oiSwapQuotes = [
	[ 2, 1, ql.Weeks, 1.245/100 ],
	[ 2, 2, ql.Weeks, 1.269/100 ],
	[ 2, 3, ql.Weeks, 1.277/100 ],
	[ 2, 1, ql.Months, 1.281/100 ],
	[ 2, 2, ql.Months, 1.18/100 ],
	[ 2, 3, ql.Months, 1.143/100 ],
	[ 2, 4, ql.Months, 1.125/100 ],
	[ 2, 5, ql.Months, 1.116/100 ],
	[ 2, 6, ql.Months, 1.111/100 ],
	[ 2, 7, ql.Months, 1.109/100 ],
	[ 2, 8, ql.Months, 1.111/100 ],
	[ 2, 9, ql.Months, 1.117/100 ],
	[ 2, 10, ql.Months, 1.129/100 ],
	[ 2, 11, ql.Months, 1.141/100 ],
	[ 2, 12, ql.Months, 1.153/100 ],
	[ 2, 15, ql.Months, 1.218/100 ],
	[ 2, 18, ql.Months, 1.308/100 ],
	[ 2, 21, ql.Months, 1.407/100 ],
	[ 2, 2, ql.Years, 1.510/100 ],
	[ 2, 3, ql.Years, 1.916/100 ],
	[ 2, 4, ql.Years, 2.254/100 ],
	[ 2, 5, ql.Years, 2.523/100 ],
	[ 2, 6, ql.Years, 2.746/100 ],
	[ 2, 7, ql.Years, 2.934/100 ],
	[ 2, 8, ql.Years, 3.092/100 ],
	[ 2, 9, ql.Years, 3.231/100 ],
	[ 2, 10, ql.Years, 3.380/100 ],
	[ 2, 11, ql.Years, 3.457/100 ],
	[ 2, 12, ql.Years, 3.544/100 ],
	[ 2, 15, ql.Years, 3.702/100 ],
	[ 2, 20, ql.Years, 3.703/100 ],
	[ 2, 25, ql.Years, 3.541/100 ],
	[ 2, 30, ql.Years, 3.369/100 ]]
 
    swapQuotes = [
	[ 2, 3, ql.Months, 1, ql.Years, 1.867/100 ],
	[ 2, 3, ql.Months, 15, ql.Months, 1.879/100 ],
	[ 2, 3, ql.Months, 18, ql.Months, 1.934/100 ],
	[ 2, 3, ql.Months, 21, ql.Months, 2.005/100 ],
	[ 2, 3, ql.Months, 2, ql.Years, 2.091/100 ],
	[ 2, 3, ql.Months, 3, ql.Years, 2.435/100 ],
	[ 2, 3, ql.Months, 4, ql.Years, 2.733/100 ],
	[ 2, 3, ql.Months, 5, ql.Years, 2.971/100 ],
	[ 2, 3, ql.Months, 6, ql.Years, 3.174/100 ],
	[ 2, 3, ql.Months, 7, ql.Years, 3.345/100 ],
	[ 2, 3, ql.Months, 8, ql.Years, 3.491/100 ],
	[ 2, 3, ql.Months, 9, ql.Years, 3.620/100 ],
	[ 2, 3, ql.Months, 10, ql.Years, 3.733/100 ],
	[ 2, 3, ql.Months, 12, ql.Years, 3.910/100 ],
	[ 2, 3, ql.Months, 15, ql.Years, 4.052/100 ],
	[ 2, 3, ql.Months, 20, ql.Years, 4.073/100 ],
	[ 2, 3, ql.Months, 25, ql.Years, 3.844/100 ],
	[ 2, 3, ql.Months, 30, ql.Years, 3.687/100 ]]

    return MarketData([Datum(numSettlementDays,timeUnit,numTimeUnits,rate) 
                 for [numSettlementDays,numTimeUnits,timeUnit,rate] in depoQuotes],
                [Datum(numSettlementDays,timeUnit,numTimeUnits,rate)
                 for [numSettlementDays,numTimeUnits,timeUnit,rate] in oiSwapQuotes],
                [SwapDatum(settlementDays,indexTimeUnit,numIndexUnits,
                           termTimeUnits,numTermUnits,rate) 
                 for [settlementDays,numIndexUnits,indexTimeUnit,numTermUnits,termTimeUnits,rate] 
                 in swapQuotes])




def getBBMarketData():
    depoQuotes =  [
	[ 0, 1, ql.Days, -0.00057 ]]
	

        
    oiSwapQuotes = [
	[ 2, 1, ql.Weeks, -0.00056 ],
	[ 2, 2, ql.Weeks, -0.00056 ],
	[ 2, 1, ql.Months, -0.00063 ],
	[ 2, 2, ql.Months, -0.00073 ],
	[ 2, 3, ql.Months, -0.00081 ],
	[ 2, 4, ql.Months, -0.00087 ],
	[ 2, 5, ql.Months, -0.00093 ],
	[ 2, 6, ql.Months, -0.00100 ],
	[ 2, 7, ql.Months, -0.00104 ],
	[ 2, 8, ql.Months, -0.00108 ],
	[ 2, 9, ql.Months, -0.00111 ],
	[ 2, 10, ql.Months, -0.00114 ],
	[ 2, 11, ql.Months,  -0.00115 ],
	[ 2, 12, ql.Months, -0.00119 ],
	[ 2, 18, ql.Months, -0.00130 ],
	[ 2, 2, ql.Years, -0.00132 ],
	[ 2, 3, ql.Years, -0.00103 ],
	[ 2, 4, ql.Years, -0.00057 ],
	[ 2, 5, ql.Years, -0.00002 ],
	[ 2, 6, ql.Years, 0.00053 ],
	[ 2, 7, ql.Years, 0.00110 ],
	[ 2, 8, ql.Years, 0.00171 ],
	[ 2, 9, ql.Years, 0.00226 ],
	[ 2, 10, ql.Years, 0.00278 ],
	[ 2, 11, ql.Years, 0.00307 ],
	[ 2, 12, ql.Years, 0.00374 ],
	[ 2, 15, ql.Years, 0.00485 ],
	[ 2, 20, ql.Years, 0.00605 ],
	[ 2, 25, ql.Years, 0.00673 ],
	[ 2, 30, ql.Years, 0.00721 ],
    [ 2, 35, ql.Years, 0.00759 ],
    [ 2, 40, ql.Years, 0.00777 ],
    [ 2, 50, ql.Years, 0.00748 ]
    ]















 
    swapQuotes = [
	[ 2, 3, ql.Months, 1, ql.Years, 1.867/100 ],
	[ 2, 3, ql.Months, 15, ql.Months, 1.879/100 ],
	[ 2, 3, ql.Months, 18, ql.Months, 1.934/100 ],
	[ 2, 3, ql.Months, 21, ql.Months, 2.005/100 ],
	[ 2, 3, ql.Months, 2, ql.Years, 2.091/100 ],
	[ 2, 3, ql.Months, 3, ql.Years, 2.435/100 ],
	[ 2, 3, ql.Months, 4, ql.Years, 2.733/100 ],
	[ 2, 3, ql.Months, 5, ql.Years, 2.971/100 ],
	[ 2, 3, ql.Months, 6, ql.Years, 3.174/100 ],
	[ 2, 3, ql.Months, 7, ql.Years, 3.345/100 ],
	[ 2, 3, ql.Months, 8, ql.Years, 3.491/100 ],
	[ 2, 3, ql.Months, 9, ql.Years, 3.620/100 ],
	[ 2, 3, ql.Months, 10, ql.Years, 3.733/100 ],
	[ 2, 3, ql.Months, 12, ql.Years, 3.910/100 ],
	[ 2, 3, ql.Months, 15, ql.Years, 4.052/100 ],
	[ 2, 3, ql.Months, 20, ql.Years, 4.073/100 ],
	[ 2, 3, ql.Months, 25, ql.Years, 3.844/100 ],
	[ 2, 3, ql.Months, 30, ql.Years, 3.687/100 ]]

    return MarketData([Datum(numSettlementDays,timeUnit,numTimeUnits,rate) 
                 for [numSettlementDays,numTimeUnits,timeUnit,rate] in depoQuotes],
                [Datum(numSettlementDays,timeUnit,numTimeUnits,rate)
                 for [numSettlementDays,numTimeUnits,timeUnit,rate] in oiSwapQuotes],
                [SwapDatum(settlementDays,indexTimeUnit,numIndexUnits,
                           termTimeUnits,numTermUnits,rate) 
                 for [settlementDays,numIndexUnits,indexTimeUnit,numTermUnits,termTimeUnits,rate] 
                 in swapQuotes])

				 
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

