import random
import ZIPlib as zippy
import ZIPimg


def game_loop():
	total_correct,total = play_one_round()
	print('you got',total_correct,'correct out of',total)

def play_one_round():
	zip_random = zippy.get_all_ZIPs()
	random.shuffle(zip_random)
	total = 0
	total_correct = 0
	for zip in zip_random:
		curr_score = play_one_zip(zip)
		if curr_score == -1:
			return total_correct,total
		else:
			total += 1
			total_correct += curr_score

def play_one_zip(zip):
	abbr_guess = ''
	print()
	while abbr_guess not in zippy.STATE_ABBR_MAP:
		print('Enter "OPT" to quit playing or "?" to view all possible abbreviations')
		abbr_guess = input('Enter the state abbreviation for ZIP code ' + zip.ZIP_code + ': ').upper()
		
		if abbr_guess == 'OPT' or abbr_guess == 'Q': return -1
		if abbr_guess == '?':
			print(zippy.state_abbrs_str())
			print()
			abbr_guess = ''


	ret_val = 0
	if zip.state_abbr == abbr_guess:
		ret_val = 1
		print( "That's right,", zip.ZIP_code, 'is in', zip.state_name(), '(' + zip.primary_city +') in the', zip.get_region_name(),'region!')
	else:
		ZIPimg.show_region(zip)
		print("Oops,",zip.ZIP_code, 'is actually in',zip.state_name(), '(' + zip.primary_city +') in the',zip.get_region_name(),'region!')
	ZIPimg.show_hulls(zip)

	return ret_val





def main():
	game_loop()

if __name__ == '__main__':
	zippy.load_ZIPs()
	main()

