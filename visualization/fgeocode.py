import aiohttp
import asyncio
import pandas as pd
import logging
import json
import requests

class ForwardGeocoderV7():
    """
    """
    def __init__(self, data, apiKey):
        self.url = "https://geocode.search.hereapi.com/v1/geocode"
        self.data = data
        self.apiKey = apiKey


    async def __fetch_address(self, session, url, params, address):
        """
        """
        async with session.get(self.url, params=params) as response:
            response = await response.text()
            result = self.__respond_parser(response)
            print(result)
            return result
    
    def __respond_parser(self, response):
        """
        """
        parsed = json.loads(response)
        
        if parsed.get("items") and len(parsed["items"]) > 0:
            parsed = parsed['items'][0]
            
            resultType = parsed.get('resultType')
            houseNumberType = parsed.get('houseNumberType')
            queryScore = parsed.get('scoring').get('queryScore')
            cityScore = parsed.get('scoring').get('fieldScore').get('city')
            houseNumberScore = parsed.get('scoring').get('fieldScore').get('houseNumber')

            streetsScore = parsed.get('scoring').get('fieldScore').get('streets')
            if streetsScore and len(streetsScore) > 0:
                streetsScore = streetsScore[0]
            else:
                streetsScore = None

            position = parsed.get("position")
            lat = position.get("lat")
            lng = position.get("lng")
            
            access = parsed.get("access")
            if access and len(access) > 0:
                access_lat = access[0].get("lat")
                access_lng = access[0].get("lng")
            else:
                access_lat = None
                access_lng = None

            g_address = parsed.get("address")
            country = g_address.get("countryName")
            admin3 = g_address.get("county")
            city = g_address.get("city")
            label = g_address.get("label")
            postalCode = g_address.get("postalCode")

            data = {
                "LABEL": label,
                "COUNTRY": country,
                "ADMIN3": admin3,
                "CITY": city,
                "POSTALCODE": postalCode,
                "LAT": lat,
                "LNG": lng,
                "ACCESS_LAT": access_lat,
                "ACCESS_LNG": access_lng,
                "RESULT_TYPE": resultType,
                "HOUSE_NUMBER_TYPE": houseNumberType,
                "QUERY_SCORE": queryScore,
                "CITY_SCORE": cityScore,
                "STREET_SCORE": streetsScore,
                "HOUSE_NUMBER_SCORE": houseNumberScore,
            }

            return data
        
        else:
            data = {
                "LABEL": None,
                "COUNTRY": None,
                "ADMIN3": None,
                "CITY": None,
                "POSTALCODE": None,
                "LAT": None,
                "LNG": None,
                "ACCESS_LAT": None,
                "ACCESS_LNG": None,
                "RESULT_TYPE": None,
                "HOUSE_NUMBER_TYPE": None,
                "QUERY_SCORE": None,
                "CITY_SCORE": None,
                "STREET_SCORE": None,
                "HOUSE_NUMBER_SCORE": None,
            }

            return data

    
    async def main(self):
        """
        """
        tasks = list()
        async with aiohttp.ClientSession() as session:
            for address in self.data:
                params = {
                    'apiKey': self.apiKey,
                    'q': address,
                }

                tasks.append(self.__fetch_address(session, self.url, params, address))
 
            data = await asyncio.gather(*tasks)
            return data


class MyFg():
    def __init__(self, data, apiKey):
        self.url = "https://geocode.search.hereapi.com/v1/geocode"
        self.data = data
        self.apiKey = apiKey

    def __fetch_address(self, params):
        """
        """
        with requests.get(self.url, params=params) as response:
            response = response.text
            result = self.__respond_parser(response)
            return result

    def __respond_parser(self, response):
        """
        """
        parsed = json.loads(response)

        if parsed.get("items") and len(parsed["items"]) > 0:
            parsed = parsed['items'][0]

            resultType = parsed.get('resultType')
            houseNumberType = parsed.get('houseNumberType')
            queryScore = parsed.get('scoring').get('queryScore')
            cityScore = parsed.get('scoring').get('fieldScore').get('city')
            houseNumberScore = parsed.get('scoring').get('fieldScore').get('houseNumber')

            streetsScore = parsed.get('scoring').get('fieldScore').get('streets')
            if streetsScore and len(streetsScore) > 0:
                streetsScore = streetsScore[0]
            else:
                streetsScore = None

            position = parsed.get("position")
            lat = position.get("lat")
            lng = position.get("lng")

            access = parsed.get("access")
            if access and len(access) > 0:
                access_lat = access[0].get("lat")
                access_lng = access[0].get("lng")
            else:
                access_lat = None
                access_lng = None

            g_address = parsed.get("address")
            country = g_address.get("countryName")
            admin3 = g_address.get("county")
            city = g_address.get("city")
            label = g_address.get("label")
            postalCode = g_address.get("postalCode")

            data = {
                "LABEL": label,
                "COUNTRY": country,
                "ADMIN3": admin3,
                "CITY": city,
                "POSTALCODE": postalCode,
                "LAT": lat,
                "LNG": lng,
                "ACCESS_LAT": access_lat,
                "ACCESS_LNG": access_lng,
                "RESULT_TYPE": resultType,
                "HOUSE_NUMBER_TYPE": houseNumberType,
                "QUERY_SCORE": queryScore,
                "CITY_SCORE": cityScore,
                "STREET_SCORE": streetsScore,
                "HOUSE_NUMBER_SCORE": houseNumberScore,
            }

            return data

        else:
            data = {
                "LABEL": None,
                "COUNTRY": None,
                "ADMIN3": None,
                "CITY": None,
                "POSTALCODE": None,
                "LAT": None,
                "LNG": None,
                "ACCESS_LAT": None,
                "ACCESS_LNG": None,
                "RESULT_TYPE": None,
                "HOUSE_NUMBER_TYPE": None,
                "QUERY_SCORE": None,
                "CITY_SCORE": None,
                "STREET_SCORE": None,
                "HOUSE_NUMBER_SCORE": None,
            }

            return data

    def main(self):
        data = []
        for i, address in enumerate(self.data, start=1):
            params = {
                'apiKey': self.apiKey,
                'q': address,
            }
            data.append(self.__fetch_address(params))
            print(f'{i}/{len(self.data)}')
        return data
