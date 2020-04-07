import datapackage
import requests
import io


def downloadData(url : str, descriptor : str):
    """
        Returns first corrence of provided descriptor from provided url as a file handler
    """
    assets = datapackage.Package(url).resources

    for data in filter(lambda x: x.tabular and x.descriptor['name'] == descriptor, assets):
        response = requests.get(data.descriptor['path'])
        return io.StringIO(response.content.decode('utf-8'))



def downloadDataCovid():
    return downloadData("https://datahub.io/core/covid-19/datapackage.json", \
                        "time-series-19-covid-combined_csv")

def downloadDataPopulation():
    return downloadData("https://datahub.io/core/population/datapackage.json", \
                        "population_csv")
