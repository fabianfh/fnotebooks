import QuantLib as ql

def BootstrapOIS(md,mc):
    oindex = ql.Eonia()
    depoIndex = ql.Euribor3M()
    depoHelpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(quote.rate)),
                                    ql.Period(quote.numTimeUnits,quote.timeUnit),
                                    quote.numSettlementDays,
                                    depoIndex.fixingCalendar(),depoIndex.businessDayConvention(),
                                    depoIndex.endOfMonth(),depoIndex.dayCounter())
                    for quote in md.depoQuotes 
                    if ql.Period(quote.numTimeUnits,quote.timeUnit) <= ql.Period(2,ql.Days)]
   
    
    oisRateHelpers = [ql.OISRateHelper(quote.numSettlementDays,
                                    ql.Period(quote.numTimeUnits,quote.timeUnit),
                                    ql.QuoteHandle(ql.SimpleQuote(quote.rate)),
                                    oindex)
                                    for quote in md.oiSwapQuotes]

   
    oisYieldCurve = ql.PiecewiseFlatForward(ql.Settings.instance().evaluationDate,
                                            depoHelpers+oisRateHelpers,ql.Actual365Fixed());
    return oisYieldCurve



def BootstrapLIBOR(md,mc,discountCurve):
    
    index3m = ql.Euribor3M()
    #depoHelpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(quote.rate)),
    #                                ql.Period(quote.numTimeUnits,quote.timeUnit),
    #                                quote.numSettlementDays,
    #                                depoIndex.fixingCalendar(),depoIndex.businessDayConvention(),
    #                                depoIndex.endOfMonth(),depoIndex.dayCounter())
    #                for quote in md.depoQuotes 
    #                if ql.Period(quote.numTimeUnits,quote.timeUnit) <= ql.Period(2,ql.Days)]
   
    fwdStart = ql.Period(0,ql.Days)
    spread = ql.QuoteHandle(ql.SimpleQuote(0))
  
    swapRateHelpers = [ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(quote.rate)),
                                         ql.Period(quote.numTermUnits,quote.termUnit),
                                         mc.calendar,
                                         mc.fixedSwapFrequency,
                                         mc.fixedSwapConvention,
                                         mc.fixedSwapDayCount,
                                         index3m,
                                         spread, 
                                         fwdStart,
                                         ql.RelinkableYieldTermStructureHandle(discountCurve))                                        
                                         for quote in md.swapQuotes]



    libor3mYieldCurve = ql.PiecewiseFlatForward(ql.Settings.instance().evaluationDate,
                                            swapRateHelpers,ql.Actual365Fixed());
    return libor3mYieldCurve
