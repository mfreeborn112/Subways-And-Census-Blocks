import pandas as pd
import geopandas as gpd
from shapely import wkt

# 1. Read data and select columns
df = pd.read_csv('subways.csv')
df = df[['OBJECTID', 'NAME', 'the_geom', 'LINE']]

# 2. Extract latitude and longitude from the_geom column
coords = df['the_geom'].str.extract('(\-?\d+\.\d+) (\-?\d+\.\d+)')
df['longitude'], df['latitude'] = coords[0].astype(float), coords[1].astype(float)

# 3. Split LINE values and create new rows
df = df.drop('LINE', axis=1).join(df['LINE'].str.split('-').explode().rename('LINE'))

# 4. Create a stopID column
df = df.reset_index(drop=True)
df['stopID'] = df.index.map(lambda x: str(x).zfill(4))

# 5. Filter out 'Express' from the LINE column
df = df[~df['LINE'].str.contains('Express')]

# 6. Drop the 'the_geom' column
df = df.drop(columns=['the_geom'])

# 7. Convert to GeoDataFrame and save as GeoJSON
geometry = gpd.points_from_xy(df.longitude, df.latitude)
geo_df = gpd.GeoDataFrame(df, geometry=geometry)
geo_df.to_file('subwaystops.geojson', driver='GeoJSON')
