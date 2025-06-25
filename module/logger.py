class Color:
    RED            = '\033[31m'
    GREEN          = '\033[32m'
    YELLOW         = '\033[33m'
    CYAN           = '\033[36m'
    RESET          = '\033[0m'

class Log:
    @staticmethod
    def Info(str):
        print(f"{Color.GREEN}[INFO] {str}{Color.RESET}")

    @staticmethod
    def Warn(str):
        print(f"{Color.YELLOW}[WARN] {str}{Color.RESET}")

    @staticmethod
    def Error(str):
        print(f"{Color.RED}[ERROR] {str}{Color.RESET}")

    @staticmethod
    def Debug(str, mode):
        if mode == True:
            print(f"{Color.CYAN}[DEBUG] {str}{Color.RESET}")