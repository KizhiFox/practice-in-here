import asyncio
import os

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from geopy.distance import geodesic

from fgeocode import ForwardGeocoderV7, MyFg

def prepare_data (input_filename, delimiter=";", encoding='utf-8'):
    '''
    Prepare data to analyze quality of Geocoder
    '''
    
    # Read original addresses
    original_df = pd.read_csv(input_filename, delimiter=delimiter, encoding=encoding)

    # Extract list of addresses to geocode
    list_to_geocode = [row['ADDRESS'] for index, row in original_df.iterrows()]

    # Initialize geocoding service
    # fg = ForwardGeocoderV7(list_to_geocode, '0JM0F5MiF3lOZDEySf19K_LHu_6uKgaEckSk_Kz6JF8')
    fg = MyFg(list_to_geocode, 'FvNowsQrGzTMKS49TOPEcJTjOQ5sjp1KBQ7W4MqQzD8')

    # Run geocoding
    # results = asyncio.run(fg.main())
    results = fg.main()

    # Transofrm data to DataFrame 
    geocoded_df = pd.DataFrame(results)
    
    # Join two data sets
    original_df = original_df.join(geocoded_df)
    errors_df = original_df[original_df['LAT'].isnull()]
    df_to_geojson('none_points', errors_df, 'ORIGINAL_LAT', 'ORIGINAL_LNG')
    original_df = original_df.dropna(subset=['LAT'])

    original_df['distances'] = list(calculate_distance(original_df, 'ORIGINAL_LAT', 'ORIGINAL_LNG', 'LAT', 'LNG'))

    return original_df


def calculate_distance (data_frame, original_lat_col, original_lng_col, geocoded_lat_col, geocoded_lng_col):

    for index, row in data_frame.iterrows():
        
        # Get coordinates of original point
        original_lat = row[original_lat_col]
        original_lng = row[original_lng_col]

        # Get coordinates of geocoded point
        geocoded_lat = row[geocoded_lat_col]
        geocoded_lng = row[geocoded_lng_col]
        
        # Create tuples of coordinates
        original_point = (original_lat, original_lng)
        geocoded_point = (geocoded_lat, geocoded_lng)
        
        # Calculate geodesic distance and append to list
        yield round(geodesic(original_point, geocoded_point).meters, 0)


def create_error_line (data_frame, original_lat_col, original_lng_col, geocoded_lat_col, geocoded_lng_col, distance_col):
    
    # Convert Pandas DataFrame to Geopandas DataFrame
    error_df = gpd.GeoDataFrame(data=data_frame)

    # Create lists of points for comparison
    original_points_list = [point for point in zip(error_df[original_lng_col], error_df[original_lat_col])]
    geocoded_points_list = [point for point in zip(error_df[geocoded_lng_col], error_df[geocoded_lat_col])]

    # Create geometry field in existing Geopandas DataFrame
    error_df["geometry"] = [LineString(points) for points in zip(original_points_list, geocoded_points_list)]

    # Create output directory
    if not os.path.exists('results'):
        os.mkdir('results')

    # Save results to file
    error_df.to_file('results/error.geojson', driver='GeoJSON', encoding="utf-8")

def df_to_geojson (result_filename, data_frame, lat_col, lng_col):
    # Convert Pandas DataFrame to Geopandas DataFrame
    spatial_df = gpd.GeoDataFrame(data=data_frame)

    # Create geometry field in existing Geopandas DataFrame
    spatial_df["geometry"] = [Point(point) for point in zip(spatial_df[lng_col], spatial_df[lat_col])]

    # Create output directory
    if not os.path.exists('results'):
        os.mkdir('results')

    # Save results to file
    spatial_df.to_file(f'results/{result_filename}.geojson', driver='GeoJSON', encoding="utf-8")


if __name__ == '__main__':
    
    # Prepare data for analysis
    data_for_analysis = prepare_data('data.csv')

    # Create error line between points
    create_error_line(data_for_analysis, 'ORIGINAL_LAT', 'ORIGINAL_LNG', 'LAT', 'LNG', 'distances')

    # Create original points layer
    df_to_geojson('original_points', data_for_analysis, 'ORIGINAL_LAT', 'ORIGINAL_LNG')

    # Create geocoded points layer
    df_to_geojson('geocoded_points', data_for_analysis, 'LAT', 'LNG')
