from PIL import Image,ImageDraw
import ZIPlib as zippy

LAT_Y_1 = (26,304)
LAT_Y_2 = (48, 49)
LONG_X_1 = (-124,65)
LONG_X_2 = (-68,715)
LAT_LONG = 0
X_Y = 1


def real_to_img_coords(lat,long):
	x = (long - LONG_X_1[LAT_LONG]) / (LONG_X_2[LAT_LONG] - LONG_X_1[LAT_LONG]) * (LONG_X_2[X_Y] - LONG_X_1[X_Y]) + LONG_X_1[X_Y]
	y = (lat - LAT_Y_1[LAT_LONG]) / (LAT_Y_2[LAT_LONG] - LAT_Y_1[LAT_LONG]) * (LAT_Y_2[X_Y] - LAT_Y_1[X_Y]) + LAT_Y_1[X_Y]
	return (x,y)


def _open_img():
	return Image.open('us_linear_h600.png').convert('RGB')


def show_prefix_hulls(prefix):
	img = _open_img()
	draw = ImageDraw.Draw(img,'RGBA')

	_draw_prefix_hulls(prefix, draw)

	img.show()


def show_hulls(zip):
	if 'state' in zip and (zip['state'] == 'AK' or zip['state'] == 'HI'): return

	img = _open_img()
	draw = ImageDraw.Draw(img, 'RGBA')

	_draw_prefix_hulls(zip['zip'], draw)

	if 'latitude' in zip and 'longitude' in zip:
		real_point = real_to_img_coords(float(zip['latitude']), float(zip['longitude']))
		draw.ellipse([(real_point[0]-1,real_point[1]-1),(real_point[0]+1,real_point[1]+1)], fill=(255,0,0,255))

	img.show()


def _draw_prefix_hulls(zip_code, draw):
	for x in range(1,min(4,1+len(zip_code))):
		_draw_prefix_hull(zip_code[:x],x,(255,0,0,55), draw)


def _draw_prefix_hull(zip_code, prefix_digits, color, draw):
	if not zip_code[:prefix_digits] in zippy.prefixes: 
		print(zip_code + ' is not a prefix that has been computed')
		return
	hull = zippy.prefixes[zip_code[:prefix_digits]]['hull']
	polyPts = list(map(lambda zip: real_to_img_coords(float(zip['latitude']),float(zip['longitude'])),hull))
	if len(polyPts) == 0:
		return
	elif len(polyPts) == 1:
		draw.point(polyPts,fill=color)
	elif len(polyPts) == 2:
		draw.line(polyPts,fill=color)
	else:
		draw.polygon(polyPts,fill=color, outline=color)


def main(zips):
	
	stop = False

	while not stop:
		cmd = input('Enter a ZIP code or a prefix to show where it is, or OPT to quit: ').upper()
		if cmd == 'OPT' or cmd == 'Q': stop = True
		if  len(cmd) == 9 and (cmd[:5] + cmd[6:]).isnumeric() and cmd[5] == '-':
			print('That\'s a +4 ZIP code! Those are great, but I\'m ignoring the +4 for this program. My map doesn\'t have enough resolution to distinguish most of them anyway')
			cmd = cmd[:5]
		if cmd.isnumeric():
			if len(cmd) == 5:
				zip_dict = zippy.find_zip(cmd)
				if 'primary_city' in zip_dict and 'state' in zip_dict:
					print('The primary city for ZIP code is ' + zip_dict['primary_city'] +', ' + zippy.get_state_name(zip_dict['state']) + '!')
				else:
					print(cmd + ' is not a ZIP code in use today, but here\'s some information about the prefixes!')
				show_hulls(zip_dict)
			elif len(cmd) < 5:
				print('Here are the ZIP codes that start with that prefix:')
				show_prefix_hulls(cmd)
				for zip_dict in zips:
					if zip_dict['zip'][0:len(cmd)] == cmd:
						print(zip_dict['zip'] + ' in ' + zip_dict['primary_city'] + ', ' + zippy.get_state_name(zip_dict['state']))
		else:
			print('Letters? What do you think this is, Canada?')
		print()

if __name__=='__main__':
	main(zippy.get_zip_list())