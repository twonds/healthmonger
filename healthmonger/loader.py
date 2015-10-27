import csv
import os
import requests
import zipfile

# healthmonger modules
import config


def download(exists=True):
    """
    Download data sources. Uses config.DATA_SOURCES
    """
    for table, source in config.DATA_SOURCES.iteritems():
        path = config.DOWNLOAD_PATH + table
        # ensure path exists
        if not os.path.exists(path):
            os.makedirs(path)
        filename = path + "/" + os.path.basename(source[1])
        if os.path.exists(filename) and not exists:
            # Do not continue if the data exsists
            continue
        # download data
        r = requests.get(source[1])
        if r.status_code != 200:
            err_msg = 'Could not download source: {0}'.format(source[1])
            raise Exception(err_msg)

        with open(filename, 'w') as f:
            f.write(r.content)


def read():
    """
    Read data downloaded from data sources.
    """
    for table, source in config.DATA_SOURCES.iteritems():
        path = config.DOWNLOAD_PATH + table
        filename = path + "/" + os.path.basename(source[1])
        # unzip
        data = {}
        with zipfile.ZipFile(filename) as zipf:
            for name in zipf.namelist():
                with zipf.open(name) as data_file:
                    if source[0] == 'csv':
                        data[name] = []
                        for row in csv.DictReader(data_file):
                            data[name].append(row)
        yield table, data


if __name__ == '__main__':
    download()
