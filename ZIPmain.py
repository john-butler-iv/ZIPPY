import ZIPanal,ZIPimg,ZIPquiz
import ZIPlib as zippy

def main():
	stop = False
	zippy.load_ZIPs()
	while not stop:
		print('Welcome to the wonderful world of Zone Improvement Plan codes! it\'s a fun time here. What would you like to do?')
		print('  Analytics - View a summary of all ZIP codes in a relatively easy to understand manner.')
		print('  Image - See your favorite ZIP code/ZIP code prefixes on a map of the US.')
		print('  Test - Test your ZIP code knowledge! Guess which state a ZIP code belongs to.')
		print('  OPT - quit.')
		choice = input(' -  ').upper()
		if choice == 'A' or choice == 'ANAL' or choice == 'ANALYTICS':
			print()
			ZIPanal.main()
		elif choice == 'I' or choice == 'IMG' or choice == 'IMAGE':
			print()
			ZIPimg.main()
		elif choice == 'T' or choice == 'TEST':
			print()
			ZIPquiz.main()
		elif choice == 'OPT':
			stop = True
		else:
			print()


if __name__ == '__main__':
	main()