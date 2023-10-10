import pandas as pd
import geopandas as gpd

# 1. Extract data from Excel for Brooklyn's census block
df = pd.read_excel('nyc-decennialcensusdata_2010_2020_census-blocks.xlsx', sheet_name='2010 and 2020 data in 2020 geog', skiprows=1)
df = df[(df['GeogName'] == 'Brooklyn') & (df['GeogType'] == 'CB2020')]
df = df[['GEOID20', 'Pop1.1']].rename(columns={'GEOID20': 'Census Block', 'Pop1.1': 'Population'})

# 2. Process the shapefile for Brooklyn
gdf = gpd.read_file('nycb2020.shp')
brooklyn_gdf = gdf[gdf['BoroCode'] == '3']

# Calculate the centroid for each geometry
brooklyn_gdf['latitude'] = brooklyn_gdf.geometry.centroid.y
brooklyn_gdf['longitude'] = brooklyn_gdf.geometry.centroid.x

# Convert the CRS to WGS84 if it's not already
if brooklyn_gdf.crs != "EPSG:4326":
    brooklyn_gdf = brooklyn_gdf.to_crs(epsg=4326)

# Retain only necessary columns and rename 'CT2020'
brooklyn_gdf = brooklyn_gdf[['BCTCB2020','CT2020', 'latitude', 'longitude', 'geometry']].rename(columns={'CT2020': 'Census Tract'})

# Convert 'BCTCB2020' to integer for merging
brooklyn_gdf['BCTCB2020'] = brooklyn_gdf['BCTCB2020'].astype(int)

# 3. Merge the dataframe with Brooklyn's GeoDataFrame
merged_df = brooklyn_gdf.merge(df, left_on='BCTCB2020', right_on='Census Block').drop(columns=['BCTCB2020'])

# 4. Convert merged_df to a GeoDataFrame and save as GeoJSON
merged_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry')
merged_gdf.to_file('/content/brooklyn census blocks.geojson', driver='GeoJSON')
