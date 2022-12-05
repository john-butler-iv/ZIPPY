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
	if zip.state_abbr == 'AK' or zip.state_abbr == 'HI': return

	img = _open_img()
	draw = ImageDraw.Draw(img, 'RGBA')

	_draw_prefix_hulls(zip.ZIP_code, draw)

	real_point = real_to_img_coords(float(zip.latitude), float(zip.longitude))
	draw.ellipse([(real_point[0]-1,real_point[1]-1),(real_point[0]+1,real_point[1]+1)], fill=(255,0,0,255))

	img.show()


def _draw_prefix_hulls(zip_code, draw):
	for num_digits in range(1,min(4,1+len(zip_code))):
		_draw_prefix_hull(zip_code[:num_digits],num_digits,(255,0,0,55), draw)


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
		draw.polygon(polyPts,fill=color, outline=color)

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

if __name__=='__main__':
	zippy.loadZIPs()
	main()