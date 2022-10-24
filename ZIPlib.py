import csv


zips = []
prefixes = {}

IRS_PREFIXES = [
	'005', # Holtsville, NY
	'055', # Andover, MA
	'192', # Philadelphia, PA
	'375', # Memphis, TN
	'399', # Atlanta, GA
	'459', # Cincinnati, OH
	'649', # Kansas City, MO
	'733', # Austin, TX
	'842', # Ogden, UT
	'928' # Fresno, CA
]

MILIARTY_PREFIXES = [
	'09' , # 
	'962', # Korea
	'963', # Japan
	'964', # Philippines
	'965', # Pacific & Antarctic bases
	'966'  # Naval/Marine
]

stAbbrMap = {
	'AL':'Alabama',
	'AK':'Alaska',
	'AZ':'Arizona',
	'AR':'Arkansas',
	'CA':'California',
	'CO':'Colorado',
	'CT':'Connecticut',
	'DE':'Delaware',
	'DC':'District of Columbia',
	'FL':'Florida',
	'GA':'Georgia',
	'HI':'Hawaii',
	'ID':'Idaho',
	'IL':'Illinois',
	'IN':'Indiana',
	'IA':'Iowa',
	'KS':'Kansas',
	'KY':'Kentucky',
	'LA':'Louisiana',
	'ME':'Maine',
	'MD':'Maryland',
	'MA':'Massachusetts',
	'MI':'Michigan',
	'MN':'Minnesota',
	'MS':'Mississippi',
	'MO':'Missouri',
	'MT':'Montana',
	'NE':'Nebraska',
	'NV':'Nevada',
	'NH':'New Hampshire',
	'NJ':'New Jersey',
	'NM':'New Mexico',
	'NY':'New York',
	'NC':'North Carolina',
	'ND':'North Dakota',
	'OH':'Ohio',
	'OK':'Oklahoma',
	'OR':'Oregon',
	'PA':'Pennsylvania',
	'RI':'Rhode Island',
	'SC':'South Carolina',
	'SD':'South Dakota',
	'TN':'Tennessee',
	'TX':'Texas',
	'UT':'Utah',
	'VT':'Vermont',
	'VA':'Virginia',
	'WA':'Washington',
	'WV':'West Virginia',
	'WI':'Wisconsin',
	'WY':'Wyoming'
}

def get_zip_region(zip):
	region = int(zip['zip'][0:1])
	if region == 0:
		return 'New England'
	if region == 1:
		return 'Mid Atlantic'
	if region == 2:
		return 'South Atlantic'
	if region == 3:
		return 'Deep South'
	if region == 4:
		return 'Eastern Midwest'
	if region == 5:
		return 'North-Western Midwest'
	if region == 6:
		return 'South-Western Midwest'
	if region == 7:
		return 'Western South'
	if region == 8:
		return 'Rockies'
	if region == 9:
		return 'Pacific'
	return ''


def print_state_abbrs():
	for abbr in stAbbrMap:
		print(abbr,'-',stAbbrMap[abbr])

def get_state_name(zip):
	stAbbr = zip
	if 'state' in zip:
		stAbbr = zip['state']

	if stAbbr in stAbbrMap:
		return stAbbrMap[stAbbr]
	return stAbbr

def get_primary_city(zip):
	prim_city = ''
	if 'primary_city' in zip:
		prim_city = zip['primary_city']
	return prim_city

def get_zip_list(disallowed_prefixes=[],filename='zip_code_database.csv'):
	read_raw(filename)
	_cull_entries(disallowed_prefixes)
	_process_prefixes()
	return zips

def find_zip(zip_code):
	# I could build an index, but eh...
	for zip in zips:
		if zip['zip'] == zip_code: return zip
	return {'zip':zip_code}

def read_raw(filename = "zip_code_database.csv"):

	with open(filename) as ZIPFile:
		ZIPReader = csv.DictReader(ZIPFile)
		for row in ZIPReader:
			zips.append(row)
	return zips

def _cull_entries(disallowed_prefixes):
	indexesToDelete = []
	for i in range(0,len(zips)):
		if should_be_culled(zips[i], disallowed_prefixes):
			indexesToDelete.append(i)
	for index in reversed(indexesToDelete):
		del zips[index]

def should_be_culled(zip, diallowed_prefixes):
	if zip['decommissioned'] == '1': return True
	if zip['state'] not in stAbbrMap: return True
	if zip_any_prefix(diallowed_prefixes, zip): return True
	if zip_any_prefix(IRS_PREFIXES + MILIARTY_PREFIXES, zip): return True

	return False

def zip_any_prefix(prefixes, zip):
	for prefix in prefixes:
		if zip_prefixed(prefix, zip):
			return True
	return False

def zip_prefixed(prefix, zip):
	return zip['zip'][:len(prefix)] == prefix


def _process_prefixes():
	prefixes.update(_group_prefixes(1))
	prefixes.update(_group_prefixes(2))
	prefixes.update(_group_prefixes(3))

	for prefix in prefixes:
		_compute_convex_hull(prefixes[prefix])
	return prefixes

def _group_prefixes(num_digits):
	local_prefixes = {}
	for zip_dict in zips:
		if zip_dict['state'] == 'HI' or zip_dict['state'] == 'AK': continue # my map doesn't show Hawaii or Alaska
		if zip_dict['zip'][:3] == '569': continue # parcel return
		if zip_dict['zip'] == '88888': continue # North Pole
		if float(zip_dict['latitude']) == 0: continue
		if float(zip_dict['longitude']) == 0: continue

		prefix_digits = zip_dict['zip'][:num_digits]
		if prefix_digits in local_prefixes:
			local_prefixes[prefix_digits]['zips'].append(zip_dict)
		else:
			local_prefixes[prefix_digits] = {'zips':[zip_dict]}
	return local_prefixes


def _compute_convex_hull(prefix):
	prefix['zips'] = sorted(prefix['zips'], key=lambda x: x['latitude'])

	top_hull = _compute_hull(prefix['zips'], True)
	bottom_hull = _compute_hull(prefix['zips'], False)


	prefix['hull'] = top_hull + list(reversed(bottom_hull[1:-1]))


def _compute_hull(sorted_zips,isTop):
	hull = []
	peak_i = 0
	for zip in sorted_zips:
		if len(hull) > 0 and zip['latitude'] == hull[-1]['latitude'] and zip['longitude'] == hull[-1]['longitude']:
			continue

		while len(hull) - 1 > peak_i and _cmp(zip, hull[-1], isTop):
			del hull[-1]

		if len(hull) == 0 or _cmp(zip, hull[peak_i], isTop) or (zip['longitude'] == hull[peak_i]['longitude'] and zip['latitude'] != hull[peak_i]['latitude']):
			peak_i = len(hull)
		
		hull.append(zip)

	
	return hull

def _cmp(zip1, zip2, use_greater):
	if use_greater:
		return float(zip1['longitude']) > float(zip2['longitude'])
	return float(zip1['longitude']) < float(zip2['longitude'])
