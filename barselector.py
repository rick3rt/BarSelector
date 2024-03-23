import pandas as pd
import geopy.distance
import json
from geopy.geocoders import Nominatim


def lookupGPSCoordinates(address):
    geolocator = Nominatim(user_agent="barselector")
    location = geolocator.geocode(address)
    return location.latitude, location.longitude


class BarSelector:
    def __init__(self):
        self.loadBars()

    def loadBars(self, filename="data/cafes.csv"):
        self.df = pd.read_csv(filename)
        self.df_clean = self.df.copy()

        self.type_filter = []
        self.distance_filter = None

        # remove columns gps_coordinates, types, address, open_state, hours,
        # operating_hours, phone, website, service_options
        self.df_clean.drop(
            columns=[
                "gps_coordinates",
                "types",
                "address",
                "open_state",
                "hours",
                "operating_hours",
                "phone",
                "website",
                "service_options",
            ],
            inplace=True,
        )

        # get all bar types from df
        self.bar_types = []
        for i in range(len(self.df_clean)):
            types = self.df_clean["type"][i]
            if pd.isna(types):
                continue
            types = types.split(",")
            for t in types:
                t = t.strip()
                if t not in self.bar_types:
                    self.bar_types.append(t)

    def getTypes(self):
        return self.bar_types

    def computeDistance(self, address):
        lat, lon = lookupGPSCoordinates(address)
        self.computeDistanceCoordinates(lat, lon)

    def computeDistanceCoordinates(self, lat, lon):
        # compute distance to all bars
        lat_lon = self.df["gps_coordinates"]
        lat_lon = lat_lon.apply(lambda x: json.loads(x.replace("'", '"')))
        self.df_clean["distance"] = lat_lon.apply(
            lambda x: geopy.distance.distance(
                (lat, lon), (x["latitude"], x["longitude"])
            ).km
        )

    def setTypeFilter(self, filter):
        self.type_filter = filter

    def setDistanceFilter(self, distance):
        self.distance_filter = distance

    def filterBars(self):
        # apply current filters
        df_filtered = self.df_clean.copy()
        if self.distance_filter is not None and "distance" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["distance"] < self.distance_filter]
        if self.type_filter:
            # get mask of bars that match filter
            df_filtered = df_filtered[
                self.df["types"].apply(lambda x: any(t in x for t in self.type_filter))
            ]
        return df_filtered

    def getWebsite(self, title):
        return self.df[self.df["title"] == title]["website"].values[0]

    def getEntry(self, title):
        return self.df[self.df["title"] == title].iloc[0].to_dict()


if __name__ == "__main__":
    bs = BarSelector()
    bs.setTypeFilter(["Cocktail"])
    bs.filterBars()
