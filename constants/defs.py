import os, shutil

LOGIN = 24651767
PASSWORD = "Windows@0806"
SERVER = "Deriv-Demo"
TIMEOUT = 60000

SYMBOL_FILTERS = "*USD*, *EUR*, *GBP*, *JPY*, *NZD*, *CAD*, *AUD*, *CHF*"
PREFERRED_SYMBOLS = ['USD', 'EUR', 'GBP', 'JPY', 'NZD', 'CAD', 'AUD', 'CHF', 'XAU', 'XAG']
PREFERRED_SYMBOLS = ['USD', 'EUR', 'GBP', 'JPY']
# PREFERRED_SYMBOLS = ['USD', 'EUR']

TIMEFRAMES = {
    # "M1" : 1,
    # "M2" : 2,
    # "M3" : 3,
    # "M4" : 4,
    # "M5" : 5,
    # "M6" : 6,
    "M10" : 10,
    "M12" : 12,
    "M15" : 15,
    "M20" : 20,
    "M30" : 30,
    "H1" : 1  | 0x4000,
    "H2" : 2  | 0x4000,
    "H4" : 4  | 0x4000,
    "H3" : 3  | 0x4000,
    "H6" : 6  | 0x4000,
    "H8" : 8  | 0x4000,
    "H12" : 12 | 0x4000,
    "D1" : 24 | 0x4000,
    "W1" : 1  | 0x8000,
    "MN1" : 1  | 0xC000,
}

TIMEFRAME_LIST = ["M15", "H1", "H4"]
MA_LONG = [i for i in [ i for i in range(200) if i% 20 == 0] if i != 0]
MA_SHORT = [i for i in [ i for i in range(50) if i% 10 == 0] if i != 0]
SIMULATED_RESULTS_FILE_PATH = './data/simulation/results/'
SIMULATED_EXCEL_RESULTS_FILE_PATH = './data/simulation/excel_sheets/'
HISTORICAL_DATA_FILE_PATH = './data/historical_data/'

# Clear Data Folder
def flush_data_dir(folder_path=HISTORICAL_DATA_FILE_PATH):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
