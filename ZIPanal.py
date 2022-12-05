import ZIPlib as zippy


def _list_by_range():
	ZIPs = zippy.get_all_ZIPs()
	start_of_range = ZIPs[0]
	last_zip = ZIPs[0]
	for zip in ZIPs[1:]:
		if zip.state_abbr != start_of_range.state_abbr:
			if start_of_range.ZIP_code != last_zip.ZIP_code:
				print(start_of_range.ZIP_code,'-',last_zip.ZIP_code + ':', last_zip.state_name())
			else:
				print('       ',start_of_range.ZIP_code+':', last_zip.state_name())
			start_of_range = zip
		
		last_zip = zip
	print(start_of_range.ZIP_code,'-',ZIPs[-1].ZIP_code + ':', start_of_range.state_name())


def _list_by_state():
	state_ix = {}
	for state in zippy.STATE_ABBR_MAP:
		state_ix[state] = {
			'state': state,
			'list': []
		}

	ZIPs = zippy.get_all_ZIPs()
	start_of_range = ZIPs[0]
	last_zip = ZIPs[0]
	for zip in ZIPs[1:]:
		if zip.state_abbr != start_of_range.state_abbr:
			state_ix[start_of_range.state_abbr]['list'].append({
				'start': start_of_range.ZIP_code,
				'end': last_zip.ZIP_code
			})
			start_of_range = zip
		
		last_zip = zip

	state_ix[start_of_range.state_abbr]['list'].append({
		'start': start_of_range.ZIP_code,
		'end': last_zip.ZIP_code
	})

	state_list = [state_ix[st] for st in state_ix]

	state_list = sorted(state_list,key=lambda st: int(st['list'][0]['start']))
	for state in state_list:
		print(zippy.STATE_ABBR_MAP[state['state']] + ':')
		for range_obj in state['list']:
			print('\t' + range_obj['start'] + '-' + range_obj['end'])


	


def main():
	stop = False

	while not stop:
		choice = input('Would you like to show all ZIP codes by [r]ange or by [s]tate? You can also type OPT to quit.\n    - ').upper()
		if choice == 'OPT' or choice == 'Q':
			stop = True
		elif choice == 'R' or choice == 'RANGE':
			_list_by_range()
		elif choice == 'S' or choice == 'STATE':
			_list_by_state()
		print()

if __name__=='__main__':
	zippy.load_ZIPs()
	main()