import json, numpy, os, PIL, random, re, requests, sys, tweepy, urllib2
sys.path.insert(0,'/root/bots/')
import sheetstation
from PIL import Image

USERS = sheetstation.get_sheet('API Master Sheet','1')
CON_KEYS = sheetstation.get_sheet('API Master Sheet','2')
CON_SECS = sheetstation.get_sheet('API Master Sheet','3')
ACCESS_KEYS = sheetstation.get_sheet('API Master Sheet','4')
ACCESS_SECS = sheetstation.get_sheet('API Master Sheet','5')


INDEX = USERS.index("@general_caution")
CATEGORIES = sheetstation.get_sheet('OpenClip Categories','1')
DANGERS = ['Hazard: ','Danger: ','Caution: ','Increased Risk Of ']
BANS = ['outline of','outline','silhouette','pattern']

CON_KEY = CON_KEYS[INDEX]
CON_SEC = CON_SECS[INDEX]
ACCESS_KEY = ACCESS_KEYS[INDEX]
ACCESS_SEC = ACCESS_SECS[INDEX]

def getOpenClipArt(item):
	matches = ""
	try:
		matches = requests.get("https://openclipart.org/search/json/?query="+item.lower()+"&amount=200")
		choices = json.loads(matches.content)
		chosen = random.randint(0,(len(choices['payload'])-1))
		return choices['payload'][chosen]['title'],choices['payload'][chosen]['svg']['png_thumb']
	except: pass

def encodeTransparency(img):
	x = numpy.array(img)
	r,g,b,a = numpy.rollaxis(x,axis=-1)
	r[a==0] = 255
	g[a==0] = 255
	b[a==0] = 255
	x = numpy.dstack([r,g,b,a])
	img = Image.fromarray(x,'RGBA')
	return img

def downloadImage(item):
	image = urllib2.urlopen(item)
	filepath = item.split("/")
	filename = filepath[len(filepath)-1]
	with open('/root/bots/generalcaution/img/'+filename,'w') as imgurl:
		imgurl.write(image.read())
	base = 81
	img = Image.open('/root/bots/generalcaution/img/'+filename).convert('RGBA')
	width, height = img.size
	if width > height:
		wpct = float(base/float(width))
		hsize = int(float(height) * float(wpct))
		resized_img = img.resize((base,hsize),PIL.Image.ANTIALIAS)
	elif height > width:
		hpct = float(base/float(height))
		wsize = int(float(width) * float(hpct))
		resized_img = img.resize((wsize,base),PIL.Image.ANTIALIAS)
	else:
		resized_img = img.resize((81,81),PIL.Image.ANTIALIAS)
	resized_img = encodeTransparency(resized_img)
	resized_img.save('/root/bots/generalcaution/img/resize_'+filename,'PNG')
	os.remove('/root/bots/generalcaution/img/'+filename)
	return filename

def makeImage(icon):
	bg = Image.open('/root/bots/generalcaution/img/template/img_base.png')
	fg = Image.open('/root/bots/generalcaution/img/template/img_top.png')
	mg = Image.open(icon)
	#mg = decodeTransparency(mg)
	width, height = mg.size
	try: bg.paste(mg,(220-(width/2),110),mg)
	except:
		print sys.exc_info()[0]
		os.remove(icon)
		makeTweet()
	os.remove(icon)
	bg.paste(fg,(0,0),fg)
	bg.save('/root/bots/generalcaution/img/temp.png')

def newImage():
	title, image = getOpenClipArt(random.choice(CATEGORIES))
	resized_file = downloadImage(image)
	makeImage('/root/bots/generalcaution/img/resize_'+resized_file)
	return (random.choice(DANGERS) + title).upper(),'/root/bots/generalcaution/img/temp.png'

def checkMessage(message):
	for ban in BANS:
		message = message.replace(ban.upper(),"")
	return message.lstrip().rstrip()

def makeTweet():
	message,img = newImage()
	message = checkMessage(message)
	AUTH = tweepy.OAuthHandler(CON_KEY,CON_SEC)
	AUTH.set_access_token(ACCESS_KEY,ACCESS_SEC)
	API = tweepy.API(AUTH)
	#print message,img
	API.update_with_media(img,status=message)

if __name__ == "__main__":
	makeTweet()

#NOTES
#
#Display area: 81.50px
#Display X: 179.25px
#Display Y: 110.00px
