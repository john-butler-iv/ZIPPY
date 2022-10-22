import ZIPlib as zippy


def _list_by_range(zips):
	start_of_range = zips[0]
	last_zip = zips[0]
	for zip in zips[1:]:
		if zip['state'] != start_of_range['state']:
			print(start_of_range['zip'],'-',last_zip['zip'] + ':', zippy.get_state_name(start_of_range))
			start_of_range = zip
		
		last_zip = zip
	print(start_of_range['zip'],'-',zips[-1]['zip'] + ':', zippy.get_state_name(start_of_range))


def _list_by_state(zips):
	state_ix = {}
	for state in zippy.stAbbrMap:
		state_ix[state] = {
			'state': state,
			'list': []
		}

	start_of_range = zips[0]
	last_zip = zips[0]
	for zip in zips[1:]:
		if zip['state'] != start_of_range['state']:
			state_ix[start_of_range['state']]['list'].append({
				'start': start_of_range['zip'],
				'end': last_zip['zip']
			})
			start_of_range = zip
		
		last_zip = zip

	state_ix[start_of_range['state']]['list'].append({
		'start': start_of_range['zip'],
		'end': last_zip['zip']
	})

	state_list = [state_ix[st] for st in state_ix]

	state_list = sorted(state_list,key=lambda st: int(st['list'][0]['start']))
	for state in state_list:
		print(zippy.get_state_name(state['state'])+':')
		for range_obj in state['list']:
			print('\t' + range_obj['start'] + '-' + range_obj['end'])


	


def main(zips):
	stop = False

	while not stop:
		choice = input('Would you like to show all ZIP codes by [r]ange or by [s]tate? You can also type OPT to quit.\n    - ').upper()
		if choice == 'OPT' or choice == 'Q':
			stop = True
		elif choice == 'R' or choice == 'RANGE':
			_list_by_range(zips)
		elif choice == 'S' or choice == 'STATE':
			_list_by_state(zips)
		print()

if __name__=='__main__':
	main(zippy.get_zip_list())