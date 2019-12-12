class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    black='\033[30m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'
    purple='\033[35m'
    cyan='\033[36m'
    lightgrey='\033[37m'
    darkgrey='\033[90m'
    lightred='\033[91m'
    lightgreen='\033[92m'
    yellow='\033[93m'
    lightblue='\033[94m'
    pink='\033[95m'
    lightcyan='\033[96m'

    @staticmethod
    def warn(a:str):
        return f'{bcolors.WARNING}{a}{bcolors.ENDC}'
    
    @staticmethod
    def fail(a:str):
        return f'{bcolors.FAIL}{a}{bcolors.ENDC}'
    
    @staticmethod
    def green(a:str):
        return f'{bcolors.OKGREEN}{a}{bcolors.ENDC}'
    
    @staticmethod
    def blue(a: str):
        return f'{bcolors.OKBLUE}{a}{bcolors.ENDC}'
    
    @staticmethod
    def header(a: str):
        return f'{bcolors.HEADER}{a}{bcolors.ENDC}'
    
    @staticmethod
    def color(a: str, color: str):
        return f'{color}{a}{bcolors.ENDC}'