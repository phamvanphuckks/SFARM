from colorama import Fore, Back, Style,init
init()
print(Fore.RED + 'some red text')
print(Fore.GREEN + 'and with a green background')
print(Style.BRIGHT + 'and in dim text')
print(Style.RESET_ALL)
print('back to normal now')
# from colorama import init
# from termcolor import colored

# # use Colorama to make Termcolor work on Windows too
# init()

# # then use Termcolor for all colored text output
# print(colored('Hello, World!', 'red'))