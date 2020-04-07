from   preloader import PreLoader
import pandas    as     pd
import numpy     as     np

class Timeseries:
    def __init__(self, country : str):

        PreLoader.init()
        self.df = PreLoader.get(country)
        self.calculateStatistics()


    def calculateStatistics(self):
        # Remove all entries with confimed == 0 (except for the last occurrence)
        self.df.reset_index(drop=True, inplace=True)
        try:
            self.df = self.df.iloc[self.df[self.df["Confirmed"] == 0].index.max():].copy()
            self.df.reset_index(drop=True, inplace=True)
        except:
            pass

        # Add Statistics
        self.df["Active"                    ] =         self.df["Confirmed"    ] - self.df["Recovered"] - self.df["Deaths"]

        self.df["Active(%)"                 ] = 100.0 * self.df["Active"       ] / self.df["Population"]
        self.df["Confirmed(%)"              ] = 100.0 * self.df["Confirmed"    ] / self.df["Population"]
        self.df["Recovered(%)"              ] = 100.0 * self.df["Recovered"    ] / self.df["Population"]
        self.df["Deaths(%)"                 ] = 100.0 * self.df["Deaths"       ] / self.df["Population"]

        self.df["Active/Confirmed(%)"       ] = 100.0 * self.df["Recovered"    ] / self.df["Confirmed"]
        self.df["Recovered/Confirmed(%)"    ] = 100.0 * self.df["Recovered"    ] / self.df["Confirmed"]
        self.df["Deaths/Confirmed(%)"       ] = 100.0 * self.df["Deaths"       ] / self.df["Confirmed"]

        self.df["New Active"                ] =         self.df["Active"       ].diff().fillna(0).astype(np.int)
        self.df["New Confirmed"             ] =         self.df["Confirmed"    ].diff().fillna(0).astype(np.int)
        self.df["New Recovered"             ] =         self.df["Recovered"    ].diff().fillna(0).astype(np.int)
        self.df["New Deaths"                ] =         self.df["Deaths"       ].diff().fillna(0).astype(np.int)
        self.df["New Active/Active(%)"      ] = 100.0 * self.df["New Active"   ] / self.df["Active"]
        self.df["New Confirmed/Active(%)"   ] = 100.0 * self.df["New Confirmed"] / self.df["Active"]
        self.df["New Recovered/Active(%)"   ] = 100.0 * self.df["New Recovered"] / self.df["Active"]
        self.df["New Deaths/Active(%)"      ] = 100.0 * self.df["New Deaths"   ] / self.df["Active"]


    @staticmethod
    def calculateOffset(list_timeseries = []):
        if len(list_timeseries) == 0:
            return []

        column_minimize = "Confirmed(%)"
        result          = [0] * len(list_timeseries)
        idx_smallest    = np.argmin(map(lambda x: len(x.df[column_minimize]), list_timeseries))
        offset_max      = len(list_timeseries[idx_smallest].df[column_minimize])

        for i, series in enumerate(list_timeseries):
            list_offsets = range(-len(series.df[column_minimize]), len(series.df[column_minimize])+1)
            list_errors  = [float("inf")] * len(list_offsets)

            for j, offset in enumerate(list_offsets):
                diffs = series.df[column_minimize].shift(periods=offset, axis="rows", fill_value=float("NaN")) \
                      - list_timeseries[idx_smallest].df[column_minimize]
                diffs = diffs.dropna()

                if len(diffs) >= (offset_max * 0.90):
                    list_errors[j] = np.power(diffs, 2).sum()

            result[i] = list_offsets[np.argmin(list_errors)]

        return result
