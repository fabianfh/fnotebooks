
# from mdb_api_client.rest_api_client import DeloitteMarketDataAPIClient


# test = DeloitteMarketDataAPIClient()
# res= test.bloomberg_get_all_markets_currencies()
# print(res)

import refinitiv.data as rd

rd.open_session()
df = rd.get_data(
        universe=['EUROSTR='], 
        fields=['TRDPRC_1']
    )
print(df)

