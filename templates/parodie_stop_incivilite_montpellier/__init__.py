import os
import sys
import math
import json
import geopy
import random
import urllib.request
import geopy.distance


from PIL import Image, ImageDraw, ImageFont

CITYLIST = "https://vigilo-bf7f2.firebaseio.com/citylist.json"
CATEGORY = 2

DELTAX = 50
DELTAY = 230

GRIDX = 1054
GRIDY = 230
MOSAICSPACE = 13
APPROXWIDTH = 936
APPROXHEIGHT = 446
COLOR = (228, 6, 19)
memx = 0
memy = 0

maxnbcols = 4
maxnblines = 4

PV = 135

LEFTTOPTITLE = "Exemple campagne de sensibilisation de la ville"
LEFTTOPTITLE_X = DELTAX
LEFTTOPTITLE_Y = 30

RIGHTTOPTITLE = "La réalité sur le terrain !\nUn total de {total} incivilités, soit {cout} €\nSomme qui pourrait être utilisé pour améliorer\nles infrastructures afin d'éviter que cela se reproduise"
RIGHTTOPTITLE_X = GRIDX
RIGHTTOPTITLE_Y = 30

RIGHTBOTTOMTITLE = "{near_count} incivilités sur ce secteur, soit {near_cout} €"
RIGHTBOTTOMTITLE_X = GRIDX
RIGHTBOTTOMTITLE_Y = 910

LEFTSTREET_X = DELTAX
LEFTSTREET_Y = 910

RIGHTITLE = "La réalité sur le terrain"


def downloadFile(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text


# Inpired by https://stackoverflow.com/questions/43734194/pillow-create-thumbnail-by-cropping-instead-of-preserving-aspect-ratio
class _Image(Image.Image):

    def crop_to_aspect(self, nwidth, nheight):
        wratio = self.width / nwidth
        hratio = self.height / nheight
        ratio = max(1, min(wratio, hratio))

        newwidth = self.width
        newheight = self.height
        if ratio > 1:
            newwidth = int(self.width/ratio)
            newheight = int(self.height/ratio)
            self.thumbnail((newwidth, newheight), Image.ANTIALIAS)

        cwidth = newwidth
        cheight = newheight
        if wratio > 1:
            cwidth = nwidth

        if hratio > 1:
            cheight = nheight

        img = self.crop((0.5 * (newwidth - cwidth),
                         0.5 * (newheight - cheight),
                         0.5 * (newwidth - cwidth) + cwidth,
                         0.5 * (newheight - cheight) + cheight))

        return img


Image.Image.crop_to_aspect = _Image.crop_to_aspect


def download_url(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text


def download_url_to_file(url, filename):
    urllib.request.urlretrieve(url, filename)


def get_scope_information(scopeid):
    data = download_url(CITYLIST)
    jcities = json.loads(data)

    for key in jcities.keys():
        if scopeid in jcities[key]['scope']:
            jcities[key]['api_path'] = jcities[key]['api_path'].replace(
                '%3A%2F%2F', '://')

            return jcities[key]

    return None


class TPLparodie_stop_incivilite_montpellier():
    def __init__(self):
        self.dir = os.path.dirname(__file__)

    def set_scope(self, scope):
        self.scope = scope
        self.api_path = get_scope_information(scope)['api_path']

    def info(self):
        return "Génère un poster comparatif entre la communication de la ville et la réalité du terrain"

    def download_and_resize_image(self, token, size=None):
        img_filename = f"/tmp/{token}.png"

        if not os.path.exists(img_filename):
            print(f"Download image {token}")
            photo_url = f"{self.api_path}/get_photo.php?token={token}"
            download_url_to_file(photo_url, img_filename)

        if size is None:
            return

        img_resized = f"/tmp/{token}_size_{size[0]}_{size[1]}.png"
        if os.path.exists(img_resized):
            return

        # Resize picture
        print(f"Try to resize image {token} to size_{size[0]}x{size[1]}")
        img = Image.open(img_filename)
        cropped = img.crop_to_aspect(size[0], size[1])
        cropped.save(img_resized)

#    def draw_current_incivilite(token)

    def generate(self, token):
        global memx, memy, memidx

        # Get issue information
        issue_url = f'{self.api_path}/get_issues.php?token={token}'
        data = download_url(issue_url)
        jissue = json.loads(data)

        issue = jissue[0]
        category = int(issue['categorie'])
        lat = float(issue['coordinates_lat'])
        lon = float(issue['coordinates_lon'])
        geopoint_issue = geopy.Point(lat, lon)

        if category != CATEGORY:
            raise Exception(
                f"Category no coresponding with incivility theme")

        # Select only near issues
        issues_url = f'{self.api_path}/get_issues.php?c={CATEGORY}'
        data = download_url(issues_url)
        jissues = json.loads(data)
        list_near = []
        for issue in jissues:
            geopoint_search = geopy.Point(
                float(issue['coordinates_lat']), float(issue['coordinates_lon']))
            dist = geopy.distance.distance(geopoint_issue, geopoint_search).m
            if dist <= 500:
                self.download_and_resize_image(issue['token'])
                list_near.append(issue)

        near_count = len(list_near)
        near_cout = near_count*PV

        nblines = int(math.sqrt((near_count)))
        totalshow = near_count - (near_count % nblines)
        nbcols = int(totalshow / nblines)

        min_nbcols = min(maxnbcols, nbcols)
        min_nblines = min(maxnblines, nblines)

        stepx = int(APPROXWIDTH/min_nbcols)
        stepy = int(APPROXHEIGHT/min_nblines)
        imgsize = (stepx, stepy)
        for issue in list_near:
            self.download_and_resize_image(issue['token'], imgsize)

        # Load pictures
        background = Image.open(
            f"{self.dir}/background_v2.png").convert("RGBA")
        result = background

        idx = 0
        for x in range(min_nbcols):
            for y in range(min_nblines):
                if list_near[idx]['token'] == token:
                    memx = x
                    memy = y

                img_filename = f"/tmp/{list_near[idx]['token']}_size_{stepx}_{stepy}.png"
                thumbnail = Image.open(img_filename)
                result.paste(
                    thumbnail, (GRIDX + (x*stepx), GRIDY+(y*stepy)))

                idx += 1

        # Draw matrix red rectangle
        d = ImageDraw.Draw(result)
        d.rectangle(
            ((GRIDX-MOSAICSPACE, GRIDY-MOSAICSPACE), ((min_nbcols*stepx)+GRIDX+MOSAICSPACE, (min_nblines*stepy)+GRIDY+MOSAICSPACE)), fill=None, outline=COLOR, width=8)

        # Main picture
        boxsize = (min_nbcols*stepx, min_nblines*stepy)
        self.download_and_resize_image(token, boxsize)
        filename = f"/tmp/{token}_size_{min_nbcols*stepx}_{min_nblines*stepy}.png"
        picture = Image.open(filename).convert("RGBA")
        smiley = Image.open(f"{self.dir}/smiley.png").convert("RGBA")
        result.paste(picture, (DELTAX, DELTAY))

        # Draw main picture red rectangle
        d.rectangle(
            ((DELTAX-MOSAICSPACE, DELTAY-MOSAICSPACE), (picture.size[0]+DELTAX+MOSAICSPACE, picture.size[1]+DELTAY+MOSAICSPACE)), fill=None, outline=COLOR, width=8)

        # Add smiley
        swidth, sheight = smiley.size
        sratio = swidth / sheight
        swidth = int(picture.size[0] * .3)
        sheight = int(swidth / sratio)

        randx = random.randint(0, picture.size[0]-swidth)
        randy = random.randint(0, picture.size[1]-sheight)
        smiley = smiley.resize((swidth, sheight))
        result.paste(smiley, (DELTAX + randx, DELTAY+randy), smiley)

        reducesmiley = smiley
        reducesmiley = reducesmiley.resize((
            int(swidth/min_nbcols), int(sheight/min_nblines)))
        result.paste(reducesmiley, (GRIDX + int((stepx*memx)),
                                    GRIDY+int((stepy*memy))), reducesmiley)

        # Draw text
        fnt40 = ImageFont.truetype(f'{self.dir}/Cantarell-Regular.otf', 40)
        d = ImageDraw.Draw(result)

        # Draw left title
        d.text((LEFTTOPTITLE_X-MOSAICSPACE, LEFTTOPTITLE_Y), LEFTTOPTITLE,
               font=fnt40, fill=(30, 30, 30, 255))

        # Draw right title
        total = len(jissues)
        cout = total*PV
        compute_title = RIGHTTOPTITLE.replace('{total}', str(total))
        compute_title = compute_title.replace(
            '{cout}', f'{cout :7,.0f}'.replace(',', '.'))
        d.text((RIGHTTOPTITLE_X-MOSAICSPACE, RIGHTTOPTITLE_Y), compute_title,
               font=fnt40, fill=(30, 30, 30, 255))

        # Street information
        d.text((LEFTSTREET_X-MOSAICSPACE, LEFTSTREET_Y), f"Proche {jissue[0]['address']}",
               font=fnt40, fill=(60, 60, 60, 255))

        # Total
        compute_title = RIGHTBOTTOMTITLE.replace(
            '{near_count}', str(near_count))
        compute_title = compute_title.replace(
            '{near_cout}', f'{near_cout: 7,.0f}'.replace(',', '.'))
        d.text((RIGHTBOTTOMTITLE_X-MOSAICSPACE, RIGHTBOTTOMTITLE_Y), compute_title,
               font=fnt40, fill=(60, 60, 60, 255))

        result.save("/tmp/result.png", format="png")
