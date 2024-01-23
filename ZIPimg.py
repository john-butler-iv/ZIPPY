import json
from PIL import Image,ImageDraw
import ZIPlib as zippy

LAT_Y_1 = (49, 27)
LAT_Y_2 = (31.334, 634)
LONG_X_1 = (-124.217,37)
LONG_X_2 = (-69.231,1545)

HI_LAT_Y_1 = (19.492, 878)
HI_LAT_Y_2 = (22.036, 766)
HI_LONG_X_1 = (-159.769, 377)
HI_LONG_X_2 = (-154.941, 555)

AK_LAT_Y_2 = (61.217,818)
AK_LAT_Y_1 = (71.299,727)
AK_LONG_X_1 = (-149.895,221)
AK_LONG_X_2 = (-141,272)

LAT_LONG = 0
X_Y = 1


def real_to_img_coords(lat,long,state_abbr=''):
	if state_abbr == 'AK': return __real_to_img_coords_core(lat,long,AK_LONG_X_1, AK_LONG_X_2, AK_LAT_Y_1, AK_LAT_Y_2)
	elif state_abbr == 'HI': return __real_to_img_coords_core(lat,long,HI_LONG_X_1, HI_LONG_X_2, HI_LAT_Y_1, HI_LAT_Y_2)
	else: return __real_to_img_coords_core(lat,long,LONG_X_1, LONG_X_2, LAT_Y_1, LAT_Y_2)

def __real_to_img_coords_core(lat, long, long_x1, long_x2, lat_y1, lat_y2):
	x = (long - long_x1[LAT_LONG]) / (long_x2[LAT_LONG] - long_x1[LAT_LONG]) * (long_x2[X_Y] - long_x1[X_Y]) + long_x1[X_Y]
	y = (lat - lat_y1[LAT_LONG]) / (lat_y2[LAT_LONG] - lat_y1[LAT_LONG]) * (lat_y2[X_Y] - lat_y1[X_Y]) + lat_y1[X_Y]
	return (x,y)



def _open_img():
	#return Image.open('us_linear_h600.png').convert('RGB')
	return Image.open('USA-XX-242243.jpeg').convert('RGB')


def show_prefix_hulls(prefix):
	img = _open_img()
	draw = ImageDraw.Draw(img,'RGBA')

	_draw_prefix_hulls(prefix, draw)

	img.show()


def show_hulls(zip):

	img = _open_img()
	draw = ImageDraw.Draw(img, 'RGBA')


	_draw_prefix_hulls(zip.ZIP_code, draw)

	real_point = real_to_img_coords(float(zip.latitude), float(zip.longitude), zip.state_abbr)
	draw.ellipse([(real_point[0]-1,real_point[1]-1),(real_point[0]+1,real_point[1]+1)], fill=(255,255,0,255))

	draw_all_outlines(get_outlines(), draw)

	img.show()


def _draw_prefix_hulls(zip_code, draw):
	for num_digits in range(1,min(4,1+len(zip_code))):
		opacity=55
		if num_digits >= 3: opacity = 100
		_draw_prefix_hull(zip_code[:num_digits],num_digits,(255,0,0,opacity), draw)


def _draw_prefix_hull(zip_code, prefix_digits, color, draw):
	hull = zippy.get_hull(zip_code[:prefix_digits])
	polyPts = list(map(lambda zip: real_to_img_coords(float(zip.latitude),float(zip.longitude)),hull))
	if len(polyPts) == 0:
		return
	elif len(polyPts) == 1:
		draw.point(polyPts,fill=color)
	elif len(polyPts) == 2:
		draw.line(polyPts,fill=color)
	else:
		draw.polygon(polyPts,fill=color, outline=(255,255,0,75))
		#draw.line(polyPts, fill=(0,0,0,175))

def show_region(zip):
	Image.open(zip.get_region_name() + '.png').show()

def main():
	
	stop = False

	while not stop:
		cmd = input('Enter a ZIP code or a prefix to show where it is, or OPT to quit: ').upper()
		if cmd == 'OPT' or cmd == 'Q': stop = True
		if  len(cmd) == 9 and (cmd[:5] + cmd[6:]).isnumeric() and cmd[5] == '-':
			print('That\'s a +4 ZIP code! Those are great, but I\'m ignoring the +4 for this program. My map doesn\'t have enough resolution to distinguish most of them anyway')
			cmd = cmd[:5]
		if cmd.isnumeric():
			if len(cmd) == 5:
				zip = zippy.get_ZIP(cmd)
				if zip.primary_city != '' and zip.state_name != '':
					print('The primary city for ZIP code is ' + zip.primary_city +', ' + zip.state_name() + '!')
				else:
					print(cmd + ' is not a ZIP code in use today, but here\'s some information about the prefixes!')
				show_hulls(zip)
			elif len(cmd) < 5:
				print('Here are the ZIP codes that start with that prefix:')
				show_prefix_hulls(cmd)
				for zip in zippy.get_all_ZIPs():
					if zip.ZIP_code[:len(cmd)] == cmd:
						print(zip.ZIP_code + ' in ' + zip.primary_city + ', ' + zip.state_name())
		else:
			print('Letters? What do you think this is, Canada?')
		print()

def get_outlines():
	with open('./us-state-boundaries.json') as boundariesFile:
		outlines = json.load(boundariesFile)
	return outlines

def draw_outline(outlines,state_abbr,draw):
	state_outline = [outline['st_asgeojson']['geometry']['coordinates'] for outline in outlines if outline['stusab']==state_abbr]
	if(len(state_outline) == 0): return
	for coords in state_outline[0]:
		draw.line(coords, fill=(255,0,0,0))

def draw_all_outlines(outlines,draw):
	nonrendered_abbrs = ['VI', 'PR', 'MP', 'GU', 'AS']
	for outline in outlines:
		if outline['stusab'] in nonrendered_abbrs: continue
		geometry = outline['st_asgeojson']['geometry']
		if geometry['type'] == 'MultiPolygon':
			for hmm in geometry['coordinates']:
				for coords in hmm:
					draw_polygon(coords, draw,outline['stusab'])
		elif geometry['type'] == 'Polygon':
			for hmm in geometry['coordinates']:
				draw_polygon(hmm,draw,outline['stusab'])
		else: print('unhandles geometry type: ',geometry['type'])


def draw_polygon(coords,draw,state_abbr):
	xys = list(map(lambda long_lat: real_to_img_coords(long_lat[1], long_lat[0],state_abbr), coords))
	draw.line(xys, fill=(0,0,0,255))

if __name__=='__main__':
	zippy.loadZIPs()
	main()