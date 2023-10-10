from functools import cache

import requests
import os
import pandas as pd
from requests import Response
from typing import Union


class DeloitteMarketDataAPIClient:
    """
    This class provides an interface to the Deloitte Market Data API (DMD).

    """

    def __init__(
        self,
        token: str = None,        
        base_url_and_port: str = None,
        
    ):
        self._auth_header = {"Authorization": token or os.getenv('TOKEN')}
        self._base_url = base_url_and_port or os.getenv('BASE_URL')

    def _rest_api_request(self, endpoint: str, params: dict = None ) -> Response:
        """
        This is the general request method to our Deloitte REST API.

        Args:
            endpoint:   endpoint in our REST APi to request
            params:     parameters for our request

        Returns:
            the response object for the specific request, if the request has been successful

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = requests.get(
            url=self._base_url + endpoint,
            headers=self._auth_header,
            params=params,
            verify=False,
        )

        if response.status_code == 200:
            if response.json():
                return response
            else:
                raise KeyError(f"No data found for the given parameters: " f"{params}")
        else:
            raise ValueError(
                f"Status Code: {response.status_code} ---- Reason: {response.reason} ---- Text: {response.text}"
            )

    @cache
    def montel_get_metadata_active_contracts(self) -> pd.DataFrame():
        """
        Returns as pd.DataFrame containing the metadata for all active derivative contracts in montels database today.

        Returns:
            pd.DataFrame containing the metadata. The pd.DataFrame contains the following columns: TickerSymbol,
            FrontSymbol, MontelSymbol, MarketName, ContractName, MarketCode, FrontCode, DeliveryArea, GenericPeriod,
            CommodityGroup, CommodityType, Currency, Denomination, SpecificPeriod, ContractYear, Spread, Otc, SourceId,
            BasePeakType, ContractSize, Liquidity, TradingStart, TradingEnd, DeliveryStart, DeliveryEnd,
            MaximumAllowedDayIntervalSizeForTrades, AccessLevel.Access, AccessLevel.Delay, AccessLevel.HistoricAccess.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/montel/get-activecontracts-metadata"
        )

        df = pd.json_normalize(response.json()["Elements"])

        return df

    @cache
    def montel_get_metadata_expired_contracts(self) -> pd.DataFrame():
        """
        Returns as pd.DataFrame containing the metadata for all expired derivative contracts in montels database up to
        today.

        Returns:
            pd.DataFrame containing the metadata. The pd.DataFrame contains the following columns: TickerSymbol,
            FrontSymbol, MontelSymbol, MarketName, ContractName, MarketCode, FrontCode, DeliveryArea, GenericPeriod,
            CommodityGroup, CommodityType, Currency, Denomination, SpecificPeriod, ContractYear, Spread, Otc, SourceId,
            BasePeakType, ContractSize, Liquidity, TradingStart, TradingEnd, DeliveryStart, DeliveryEnd,
            MaximumAllowdDayIntervalSizeForTrades, AccessLevel.Access, AccessLevel.Delay, AccessLevel.HistoricAccess.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/montel/get-expiredcontracts-metadata"
        )

        df = pd.json_normalize(response.json()["Elements"])

        return df

    def montel_get_metadata_specified_contract(
        self, symbol_keys: list[str]
    ) -> pd.DataFrame():
        """
        Returns a pd.DataFrame containing the metadata for a given list of tickers. Possible kinds of tickers are:
        TickerSymbol, FrontSymbol and MontelSymbol. See Montel Web API User Guide p. 33 for further information.

        Args:
            symbol_keys:    list of strings of the respective tickers. Tickers can be found using the methods
                            montel_get_metadata_active_contracts() and montel_get_metadata_expired_contracts().

        Returns:
            pd.DataFrame containing the metadata. The pd.DataFrame contains the following columns: TickerSymbol,
            FrontSymbol, MontelSymbol, MarketName, ContractName, MarketCode, FrontCode, DeliveryArea, GenericPeriod,
            CommodityGroup, CommodityType, Currency, Denomination, SpecificPeriod, ContractYear, Spread, Otc, SourceId,
            BasePeakType, ContractSize, Liquidity, TradingStart, TradingEnd, DeliveryStart, DeliveryEnd,
            MaximumAllowedDayIntervalSizeForTrades, AccessLevel.Access, AccessLevel.Delay, AccessLevel.HistoricAccess.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if all requested tickers are wrong a KeyError is raised. Note: montel does not provide
                        any kind of information when a key without any metadata is requested.
        """

        params = {"SymbolKeys": symbol_keys}
        response = self._rest_api_request(
            endpoint="/api/montel/get-specifiedcontracts-metadata", params=params
        )

        if len(response.json()["Elements"]):
            df = pd.json_normalize(response.json()["Elements"])
            return df
        else:
            raise KeyError(f"No data found for all tickers in: {symbol_keys}")

    def montel_get_metadata_fundamentals(self) -> pd.DataFrame():
        """
        Returns a pd.DataFrame containing the metadata for all Fundamentals in Montels database. The data category
        fundamentals includes information about production, consumption, and flows from Power, Gas, Oil, and Coal, but
        EPEX Spot data can also be found here. See Montel Web API docu p.12 for further information.

        Returns:
            pd.DataFrame containing the metadata. The following columns should be present: FundamentalKey,
            Description, ExpectedElementsPerDay, ExpectedElementNames, RequiredServiceId, ProductSource, ProductCountry,
            ProductZone, ProductUnitLong, ProductUnitShort, IntervalType, IntervalValue, Forecast, ElementType,
            ProductTimeZone, ProductTimeZoneOffset, ContentRange, ContentType, ElementGroup, PowerSource, PowerPlantName
            PowerPlantUnitName, ProductZoneTo, PowerCompanyName, StationID, StationName, FuturesSource, Pattern,
            Character, Kind, SpotSource1, SpotSource2, Resolution. Note: due to the nature of the Fundamentals it is
            expected, that per fundamental-key only a subset of these columns is filled with values.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/montel/get-fundamentals-metadata"
        )

        df = pd.DataFrame(response.json()["Elements"])
        # fix formatting of Attributes -> special to fundamentals
        for idx, row in df.iterrows():
            for attr in df["Attributes"].iloc[idx]:
                df.loc[idx, list(attr.values())[0]] = list(attr.values())[1]
        df.drop(columns=["Attributes"], inplace=True)

        return df

    def montel_get_metadata_spot(self) -> pd.DataFrame():
        """
        Returns a pd.DataFrame containing the metadata for all spot tickers in Montels database.

        Returns:
            pd.DataFrame containing the following columns: SpotKey, SpotName, SourceName, PeakType, Country,
            DefaultCurrency, AvailableCurrencies.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        response = self._rest_api_request(endpoint="/api/montel/get-spot-metadata")

        df = pd.DataFrame(response.json()["Elements"])

        return df

    def montel_get_historic_quote(
        self,
        symbol_key: str,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        add_metadata: bool = True,
        fields: list[str] = [
            "TickerSymbol",
            "ContractName",
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Settlement",
            "Volume",
            "OpenInterest",
        ],
        insert_elements_when_data_missing="never",
        continuous: bool = True,
    ) -> pd.DataFrame:
        """
        Returns a pd.DataFrame containing the historic quotes for a given Ticker [symbol_key] and time range [between
        start_date and end_date]. Possible kinds of Tickers are: TickerSymbol, FrontSymbol and MontelSymbol. See Montel
        Web API User Guide p. 33 for further information.

        Args:
            symbol_key:     ticker. Active tickers can be found using the methods montel_get_metadata_active_contracts()
                            and montel_get_metadata_expired_contracts().
            start_date:     first timestamp
            end_date:       last timestamp
            add_metadata:   boolean to specify whether the metadata of the ticker should be returned as well.
            fields:         data categories to request. Possible fields are: TickerSymbl, ContractName, Date, Open, High,
                            Low, Close, Settlement, Volume, OpenInterest. See Montel Web API docu p. 40 for further
                            information.
            insert_elements_when_data_missing: 'weekdays', 'always' or 'never'. Specifies, if the server should return
                            empty elements for days without data.
            continuous:     'true' or 'false'. Only in effect when FrontSymbol is used as a SymbolKey. If set to false:
                            API will return historic data for the contract that match the relative symbol compared to
                            today. If set to true: API will return historic data for multiple contracts chained
                            together, so that each element covers the contract that match the relative symbol compared
                            to this element’s date. See Montel Web API User Guide p. 16 for further information

        Returns:
            pd.DataFrame containing the received information. If the fields parameter is not manipulated the fields 
            'TickerSymbol', 'ContractName', 'Date', 'Open', 'High', 'Low', 'Close', 'Settlement', 'Volume',
            'OpenInterest' and 'SymbolKey' are returned. If the parameter add_metadata is set to True all metadata
            elements are returned as well. See montel_get_metadata_active_contracts() for a description of the returned
            metadata columns.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        params = {
            "SymbolKey": symbol_key,
            "Fields": fields,
            "FromDate": start_date,
            "ToDate": end_date,
            "SortType": "ascending",
            "InsertElementsWhenDataMissing": insert_elements_when_data_missing,
            "Continuous": str(continuous).lower(),
        }

        if add_metadata:
            endpoint = "/api/montel/get-future-quote-metadata"
        else:
            endpoint = "/api/montel/get-derivatives-historic-quote"
        response = self._rest_api_request(endpoint=endpoint, params=params)

        if add_metadata:
            df = pd.json_normalize(response.json())
            return df
        else:
            df = pd.DataFrame(response.json()["Elements"])
            df["SymbolKey"] = response.json()["SymbolKey"]
            return df

    def montel_get_current_quote(
        self,
        symbol_keys: list[str],
        fields: list[str] = [
            "SymbolKey",
            "TickerSymbol",
            "FrontSymbol",
            "MontelSymbol",
            "Bid",
            "BidSize",
            "BidFlow",
            "Ask",
            "AskSize",
            "AskFlow",
            "BidAskSpread",
            "Last",
            "LastVolume",
            "LastFlow",
            "AccVolume",
            "Settlement",
            "Open",
            "High",
            "Low",
        ],
    ) -> pd.DataFrame:
        """
        Returns the current quotes for a given list of tickers. Possible kinds of Tickers are: TickerSymbol, FrontSymbol
        and MontelSymbol. See Montel Web API User Guide p. 33 for further information.

        Args:
            symbol_keys:    list of tickers. Available tickers can be found using the methods
                            montel_get_metadata_active_contracts() and montel_get_metadata_expired_contracts().
            fields:         Data categories to request. Possible fields are: 'SymbolKey', 'TickerSymbol', 'FrontSymbol',
                            'MontelSymbol', 'Bid', 'BidSize', 'BidFlow', 'Ask', 'AskSize', 'AskFlow', 'BidAskSpread',
                            'Last', 'LastVolume', 'LastFlow', 'AccVolume', 'Settlement', 'Open', 'High', 'Low'. See
                            Montel Web API p. 39 for further information. The field 'UpdateTime' is always returned.

        Returns:
            pd.DataFrame containing the quotes for all requested fields. See the 'fields' parameter for a list of
            possible fields.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        params = {"SymbolKeys": symbol_keys, "Fields": fields}

        response = self._rest_api_request(
            endpoint="/api/montel/get-derivatives-quote", params=params
        )

        df = pd.DataFrame(response.json()["Elements"])

        return df

    def montel_get_fundamental_data(
        self, fundamental_key: str, start_date: pd.Timestamp, end_date: pd.Timestamp,
    ) -> pd.DataFrame:
        """
        Returns a pd.DataFrame containing the requested values for a given fundamental [fundamental_key] in a given time
        range [start_date and end_date]. The data category fundamentals includes information about production,
        consumption, and flows from Power, Gas, Oil, and Coal, but EPEX Spot data can also be found here. See Montel Web
        API docu p.28 for further information.

        Args:
            fundamental_key:    key of the fundamental. Use montel_get_metadata_fundamentals() to find fundamentals and
                                their keys.
            start_date:         first timestamp
            end_date:           last timestamp

        Returns:
            pd.DataFrame containing the columns 'FundamentalKey', 'TimeFrom', 'TimeTo' and 'Value'.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        params = {
            "FundamentalKey": fundamental_key,
            "FromDate": start_date,
            "ToDate": end_date,
            "SortType": "ascending",
        }

        response = self._rest_api_request(
            endpoint="/api/montel/get-fundamental-data", params=params
        )

        df_master = pd.DataFrame()
        for elem in response.json()["Elements"]:
            df_inner = pd.DataFrame(elem["TimeSpans"])
            df_master = pd.concat([df_master, df_inner], axis=0, ignore_index=True)
        df_master["FundamentalKey"] = response.json()["FundamentalKey"]

        return df_master.reindex(
            columns=["FundamentalKey", "TimeFrom", "TimeTo", "Value"]
        )

    def montel_get_future_quote(
        self,
        exchange_code: str,
        country_code: str,
        contract_type: str,
        contract: str,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        add_metadata: bool = True,
        fields: list[str] = [
            "TickerSymbol",
            "ContractName",
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Settlement",
        ],
        insert_elements_when_data_missing: str = "never",
        continuous: bool = True,
    ):
        """
        Returns a pd.DataFrame containing historic quotes for a futures contract, based on a given exchange
        [exchange_code], country [country_code], contract type [contract_type] and contract [contract] for a given time
        range [start_date] and [end_date].

        Args:
            exchange_code: Exchange, e.g. EEX or ICE
            country_code:  Country, e.g. de or en
            contract_type: 'base', 'peak' for all markets and 'offpeak' for a few selected markets. Use the metadata to
                           find possible types for each respective market.
            contract:      Specific contract to query. Front Codes and Montel Codes can be used.
                           Front Codes consist of one letter for the period length and one or two digits for period number.
                           E.g. the Front Code 'D1' corresponds to the Future Contract with the next day as
                           delivery period, since the letter 'D' implies the period length 'Day' and the digit '1' the
                           next full day. Likewise, M0 corresponds to the current month, i.e., the month of the given date.
                            Examples for other delivery periods:
                            (A) daily contracts:     D0, D1, ..
                            (B) weekly contracts:    W0, W1, ..
                            (C) weekend contracts:   WNKD0, WNKD1, ..
                            (D) quarterly contracts: Q1, Q2, ..
                            (E) seasonal contracts:  S1, S2, ..
                            (F) montly contracts:    M0, M1, ..
                            (G) annual contracts:    Y1, Y2, ..
                           Montel Codes are the 'ContractName'. Note, that Montel Codes have to be written in uppercase
                           and that day futures have to be translated to a specific date. 
                            Examples:
                            (A) daily contracts:      '2023-02-17'
                            (B) weekly contracts:     'WK8-2023'
                            (C) weekend contracts:    'WKND8-2023' ..
                            (D) monthly contracts:    'NOV-2023'
                            (E) quarterly contracts:  'Q3-2023'
                            (F) seasonal contracts:   'SUM-2023', 'WIN-2023'
                            (G) annual contracts:     'CAL-2023'
                           To find more Front Codes and Montel Codes use the method
                           montel_get_metadata_active_contracts().
            start_date:    first timestamp
            end_date:      last timestamp
            add_metadata:  boolean to specify whether the metadata for the respective ticker should be returned
            fields:        data categories to request. Possible fields are: TickerSymbl, ContractName, Date, Open, High,
                           Low, Close, Settlement, Volume, OpenInterest. See Montel Web API docu p. 40 for further
                           information.
            insert_elements_when_data_missing: 'weekdays', 'always' or 'never'. Specifies, if the server should return
                            empty elements for days without data.
            continuous:     'true' or 'false'. Only in effect when FrontSymbol is used as a SymbolKey. If set to false:
                            API will return historic data for the contract that match the relative symbol compared to
                            today. If set to true: API will return historic data for multiple contracts chained
                            together, so that each element covers the contract that match the relative symbol compared
                            to this element’s date. See Montel Web API User Guide p. 16 for further information.

        Returns:
            pd.DataFrame containing the

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
        """

        params = {
            "exchange_code": exchange_code,
            "country_code": country_code,
            "contract_type": contract_type,
            "contract": contract,
            "date": start_date,
            "end_date": end_date,
            "fields": fields,
            "sort_type": "ascending",
            "insert_elements_when_data_missing": insert_elements_when_data_missing,
            "continuous": str(continuous).lower(),
        }

        if add_metadata:
            endpoint = "/api/montel/get-future-quote"
        else:
            endpoint = "/api/montel/get-future-quote-without-metadata"
        response = self._rest_api_request(endpoint=endpoint, params=params)

        if add_metadata:
            df = pd.json_normalize(response.json())

            return df
        else:
            df = pd.DataFrame(response.json()["Elements"])

            return df

    def montel_get_dict_future_codes(self):
        """
        Returns a pd.DataFrame containing all available future codes.

        Returns:
            pd.DataFrame containing the future codes.
        """

        response = self._rest_api_request(endpoint="/api/montel/get-dict-of-codes")

        df = pd.json_normalize(response.json()).T

        return df

    def bloomberg_get_all_available_fields(self):
        """
        Returns a pd.DataFrame containing all available fields in our Bloomberg DB, as well as their respective
        description and definition. Fields are the data columns available in this database, e.g. 'ASK' or 'BID'.

        Returns:
            pd.DataFrame containing the columns fields_name, fields_description and fields_definition.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-all-available-fields"
        )

        df = pd.DataFrame(response.json())

        return df

    def bloomberg_get_all_available_tenors(self):
        """
        Returns a pd.DataFrame containing all available tenors in our Bloomberg DB.

        Returns:
            pd.DataFrame containing all available tenors in the column 'tenors_name'.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-all-available-tenors"
        )

        df = pd.DataFrame(response.json())

        return df

    def bloomberg_get_all_markets_currencies(self):
        """
        Returns a pd.DataFrame containing all available markets and their currencies.

        Returns:
            pd.DataFrame containing the two columns 'Market' and 'Currencies'

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-all-markets-currencies"
        )

        df = (
            pd.json_normalize(response.json())
            .T.reset_index()
            .rename(columns={"index": "Market", 0: "Currencies"})
        )

        return df

    def bloomberg_get_ticker_info(self, ticker: str):
        """
        Returns a pd.DataFrame containing basic information about the given ticker: tickerid, tickerlabel, description
        and maturity.

        Args:
            ticker: ticker for our Bloomberg DB

        Returns:
            pd.DataFrame containing the columns 'tickerid', 'tickerlabel', 'tickerdescription' and 'maturity'

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-ticker-info", params={"ticker": ticker}
        )

        df = pd.DataFrame(response.json())

        return df

    def bloomberg_get_ticker(
        self,
        market: str,
        currency: str,
        date: pd.Timestamp,
        tenor: str = None,
        field: str = None,
    ):
        """
        Returns a pd.DataFrame containing the explicit ticker price by currency, market, tenor, field and date

        Args:
            market:   market to query
            currency: currency to query
            date:     date
            tenor:    tenor to return. If no tenor is given all tenors will be returned
            field:    fields to return, e.g. HIGH, LOW, BID, MID, ASK,... If no field is given all will be returned

        Returns:
            pd.DataFrame containing: ticker_name, ticker_description, field_name, tenor, value (i.e. price) and date

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        params = {
            "market": market,
            "currency": currency,
            "date": date,
            "tenor": tenor,
            "field": field,
        }

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-ticker", params=params
        )

        df = pd.DataFrame(response.json())

        return df

    def bloomberg_get_ticker_period(
        self,
        market: str,
        currency: str,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        tenor=None,
        fields=None,
    ):
        """
        Returns a pd.DataFrame containing the prices of a ticker for a given time range [start_date and end_date], a
        given market [market] and the given currency [currency]. Tenor and fields are optional parameters

        Args:
            market: market to query, e.g. MM
            currency: currency to query, e.g. AUD
            start_date: first timestamp
            end_date:   last timestamp
            tenor:      Tenor to return. By default, all tenors will be returned
            fields:     fields to return, e.g. HIGH, LOW, BID, MID, ASK,... If no field is given all will be returned.

        Returns:
            pd.DataFrame containing: ticker_name, ticker_description, field_name, tenor, value (i.e. price) and date

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        params = {
            "market": market,
            "currency": currency,
            "start_date": start_date,
            "end_date": end_date,
            "tenor": tenor,
            "fields": fields,
        }

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-ticker-period", params=params
        )

        df = pd.DataFrame(response.json())

        return df

    def bloomberg_get_curve_data(
        self,
        currency: str,
        curve_type: str,
        curve_calc_type: str,
        date: pd.Timestamp = None,
        calc_date=None,
    ):
        """
        Get curve data by currency, curve type, curve calculation type, date and calculation date

        Args:
            currency:        currency to query, currently available:  EUR, USD, CHF and GBP
            curve_type:      curve type to query, i.e. 1M, 3M, 6M, 12M, DISCOUNT, OIS
            curve_calc_type: calc type of the curve, i.e. SINGLE, DUAL, DUAL WITH BASIS, ADJUSTED.USD
            date:            date of the data. Please note that data is only available for business dates.
                             If no value is entered the most recent date will be returned
            calc_date:       the date of the curve upload into the database. If no value is entered the most recent date
                             will be returned

        Returns:
            pd.DataFrame containing: curve_id, currency, term, discount_factor, date and calculation_date

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        params = {
            "currency": currency,
            "curve_type": curve_type,
            "curve_calc_type": curve_calc_type,
            "date": date,
            "calcdate": calc_date,
        }

        response = self._rest_api_request(
            endpoint="/api/Bloomberg/get-curve-data", params=params
        )

        df = pd.DataFrame(response.json())

        return df

    def volue_get_available_areas(self):
        """
        Returns a pd.DataFrame containing all available areas in our volue database.

        Returns:
            pd.DataFrame containing all available areas and their IDs sorted in two columns: 'id' and 'area'

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(endpoint="/api/volue/getavailableareas")

        df = pd.DataFrame(response.json())

        return df

    def volue_get_available_curve_types(self):
        """
        Returns a pd.DataFrame containing all available curve types in our volue database. A curve type references the
        type of power in the respective forward curve. Example: the curve type 'base' references the forward curve for
        baseload power prices. The curve type 'WIND_ON' references the forward curve for onshore wind power prices.

        Returns:
            pd.DataFrame containing all available curve types and their IDs and in the two columns 'id' and 'curve'

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(endpoint="/api/volue/getavailablecurvetypes")

        df = pd.DataFrame(response.json())

        return df

    def volue_get_available_scenarios(self):
        """
        Returns a pd.DataFrame containing all available scenarios inside our volue database.

        Returns:
            pd.DataFrame containing all available scenarios and their IDs in the two columns 'id' and 'scenario'

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(endpoint="/api/volue/getavailablescenarios")

        df = pd.DataFrame(response.json())

        return df

    def volue_get_available_volue_dates(self):
        """
        Returns a pd.DataFrame containing all available volue dates in our volue database. A volue date is the date of
        the corresponding volue excel export. It references the quarter in which the respective Excel output is
        generated and the volue data was obtained.

        Returns:
            pd.DataFrame containing all available volue dates in the columns 'date_WB'

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        response = self._rest_api_request(endpoint="/api/volue/getavailablevoluedates")

        df = pd.DataFrame(response.json())

        return df

    def volue_get_volue_data(
        self,
        area: list[str],
        curve: list[str],
        scenario: list[str],
        date: list[str],
        year: Union[int, str] = None,
    ):
        """
        Returns a pd.DataFrame containing the volue data for the specified arguments.

        Args:
            area:       the country for the respective forward curve. See volue_get_available_areas() for more
                        information.
            curve:      the curve type. Describes the respective forward curve. See volue_get_available_curve_types()
                        for more information.
            scenario:   the weather scenario. A scenario expresses future price expectations based on historical climate
                        data. Use volue_get_available_scenarios() to retrieve available scenarios.
            date:       the date of the curve data. See volue_get_available_volue_dates() for more information.
            year:       specify a single year if needed. By default, all years are parsed.

        Returns:
            pd.DataFrame containing the columns: id, date_wb, date_Year, data_Provider, area, curve,
            scenario and price. The prices are real prices, meaning they're inflation-adjusted by volue.

        Raises:
            ValueError: if the request hasn't been successfull, a ValueError is raised.
            KeyError:   if no data is available for the given parameters a KeyError is raised.
        """

        params = {
            "Area": area,
            "Curve": curve,
            "Scenario": scenario,
            "Date_WB": date,
            "Year": year,
        }

        response = self._rest_api_request(
            endpoint="/api/volue/getvoluedata", params=params
        )

        df = pd.DataFrame(response.json())

        return df
