import datahub
import pandas as pd
import numpy as np

"""
    Singleton class
    Initalizes with method init()
    Uses datahub to retrieve data by default
"""
class PreLoader:
    df = None

    @staticmethod
    def init(df_covid = None, df_popul = None, country_selected = [], country_aliases = None):
        # Only initialize if preloader is not initialized
        # => Only initializes once
        if PreLoader.df is None:
            if df_covid is None:
                df_covid        = pd.read_csv(datahub.downloadDataCovid())
            if df_popul is None:
                df_popul        = pd.read_csv(datahub.downloadDataPopulation())
            if country_aliases is None:
                country_aliases = { "US" : ["United States"] }

            # Prepare dataframes to have the proper schema
            df_covid, df_popul = PreLoader.prepareSchema(df_covid, df_popul, country_selected)
            # Add population values from Population dataframe
            PreLoader.df       = PreLoader.addPopulation(df_covid, df_popul, country_aliases)


    @staticmethod
    def addPopulation(df_covid, df_popul, country_aliases):
        """
            Adds population to Covid timeseries dataframe from Population dataframe
        """
        df_covid["Population"] = 0.0

        for index, row in df_covid.iterrows():
            # Get dataframe only for that specific country (Use possible aliases)
            df_aux = df_popul[df_popul["Country"].isin([row["Country"]] + country_aliases.get(row["Country"], []))]

            # Get the closest population data for each row specific date
            values = df_aux.iloc[(df_aux["Date"] - row["Date"]).abs().argsort()][:1]["Value"].values

            # Allow no data for that countries population
            assert(len(values) <= 1)
            df_covid.loc[index, "Population"] = values[0] if len(values) == 1 else float("NaN")

        return df_covid


    @staticmethod
    def prepareSchema(df_covid, df_popul, country_selected):
        """
            Removes, renames columns and changes datatypes for necessary dataframes
        """
        # Rename columns
        df_covid.rename(columns = {"Country/Region" : "Country"}      , inplace=True)
        df_covid.rename(columns = {"Province/State" : "State"  }      , inplace=True)
        df_popul.rename(columns = {"Country Name"   : "Country"}      , inplace=True)
        df_popul.rename(columns = {"Year"           : "Date"   }      , inplace=True)
        # Drop columns
        df_covid.drop(  columns = ['State', "Lat", "Long"]            , inplace=True, errors="ignore")
        df_popul.drop(  columns = ['Country Code']                    , inplace=True, errors="ignore")
        # Drop nan values
        df_covid.dropna(subset  = ['Confirmed', "Recovered", "Deaths"], inplace=True)

        # Drop all countries not selected
        if len(country_selected) == 0:
            country_selected = list(df_covid["Country"].unique())

        df_covid = df_covid[df_covid["Country"].isin(country_selected)].copy()

        # Convert columns to proper datatypes
        df_covid["Date"      ]  = df_covid["Date"     ].apply(pd.to_datetime)
        df_covid["Country"   ]  = df_covid["Country"  ].astype(pd.StringDtype())
        df_covid["Confirmed" ]  = df_covid["Confirmed"].astype(np.int)
        df_covid["Recovered" ]  = df_covid["Recovered"].astype(np.int)
        df_covid["Deaths"    ]  = df_covid["Deaths"   ].astype(np.int)

        df_popul['Date'      ]  = pd.to_datetime(df_popul['Date'], format = "%Y")
        df_popul["Value"     ]  = df_popul["Value"    ].astype(np.int)

        # Group values by Country with different regions
        df_covid = df_covid.groupby(["Date","Country"], as_index=False).sum()

        return df_covid, df_popul

    @staticmethod
    def get(country):
        return PreLoader.df[PreLoader.df["Country"] == country].copy()
