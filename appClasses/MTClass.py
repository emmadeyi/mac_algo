import constants.defs as defs
import MetaTrader5 as mt5

class MTClass:

    def __init__(self):
        self.initialize()

    # Initialize MT5
    def initialize(self):
        try:
            # Initializing
            if mt5.initialize(login=defs.LOGIN, password=defs.PASSWORD, server=defs.SERVER): 
                return "True"
            else:
                return "initialize() failed, error code =",mt5.last_error()
        except Exception as error:
            return "initialize() failed, error code =",mt5.last_error()
        
    # Get account info
    def get_account_info(self):
        account_info = mt5.account_info()
        print("Get MT5 Account Info...")
        print("========================")
        if account_info != None:
            print("name: ", account_info.name)
            print("Account: ", account_info.login)
            print("Balance: ", account_info.balance)
            print("Equity: ", account_info.equity)
            print("Profit: ", account_info.profit)
            print("Currency: ", account_info.currency)
            print("Limit Orders: ", account_info.limit_orders)
            print("Server: ", account_info.server)
            print("Company: ", account_info.company)
            print("Symbols: ", mt5.symbols_total())
            print("========================")
        else:
            print("failed to fetch account infomation")
    
    # Authorize Account
    def authorize(self):
        if mt5.login(login=defs.LOGIN, password=defs.PASSWORD, server=defs.SERVER):
            return True
        else:
            return "failed to connect to trade account, error code =", mt5.last_error()
   
    # shut down connection to the MetaTrader 5 terminal
    def shutdown(self):
        return mt5.shutdown()    
    






