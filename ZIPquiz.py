import random
import ZIPlib as zippy
import ZIPimg


def game_loop(ZIP_master):
	prefixes = zippy.process_prefixes(ZIP_master)
	total_correct,total = play_one_round(ZIP_master,prefixes)
	print('you got',total_correct,'correct out of',total)

def play_one_round(ZIP_master, prefixes):
	zip_random = ZIP_master[:]
	random.shuffle(zip_random)
	total = 0
	total_correct = 0
	for zip in zip_random:
		curr_score = play_one_zip(zip, prefixes)
		if curr_score == -1:
			return total_correct,total
		else:
			total += 1
			total_correct += curr_score

def play_one_zip(zip, prefixes):
	abbr_guess = ''
	print()
	while abbr_guess not in zippy.stAbbrMap:
		print('Enter "OPT" to quit playing or "?" to view all possible abbreviations')
		abbr_guess = input('Enter the state abbreviation for ZIP code ' + zip['zip'] + ': ').upper()
		
		if abbr_guess == 'OPT' or abbr_guess == 'Q': return -1
		if abbr_guess == '?':
			zippy.print_state_abbrs()
			print()
			abbr_guess = ''


	ret_val = 0
	if zip['state'] == abbr_guess:
		ret_val = 1
		print("That's right,", zip['zip'], 'is in', zippy.get_state_name(zip),'(' + zippy.get_primary_city(zip) +') in the',zippy.get_zip_region(zip),'region!')

	else:
		#Image.open(zippy.get_zip_region(zip) + '.png').show()
		print("Oops,",zip['zip'],'is actually in',zippy.get_state_name(zip),'(' + zippy.get_primary_city(zip) +') in the',zippy.get_zip_region(zip),'region!')

	ZIPimg.show_hulls(zip)
	return ret_val





def main(zips):
	game_loop(zips)

if __name__ == '__main__':
	main(zippy.get_zip_list())

