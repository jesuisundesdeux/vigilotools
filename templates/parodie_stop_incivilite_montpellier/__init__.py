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

DELTAX = 30
DELTAY = 30
MOSAICX = 1054
MOSAICY = 30
MOSAICSPACE = 13
APPROXWIDTH = 936
APPROXHEIGHT = 446
COLOR = (228, 6, 19)
memidx = 0
memidy = 0


def downloadFile(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text


# Source: https://stackoverflow.com/questions/43734194/pillow-create-thumbnail-by-cropping-instead-of-preserving-aspect-ratio
class _Image(Image.Image):

    def crop_to_aspect(self, aspect, divisor=1, alignx=0.5, aligny=0.5):
        """Crops an image to a given aspect ratio.
        Args:
            aspect (float): The desired aspect ratio.
            divisor (float): Optional divisor. Allows passing in (w, h) pair as the first two arguments.
            alignx (float): Horizontal crop alignment from 0 (left) to 1 (right)
            aligny (float): Vertical crop alignment from 0 (left) to 1 (right)
        Returns:
            Image: The cropped Image object.
        """
        if self.width / self.height > aspect / divisor:
            newwidth = int(self.height * (aspect / divisor))
            newheight = self.height
        else:
            newwidth = self.width
            newheight = int(self.width / (aspect / divisor))
        img = self.crop((alignx * (self.width - newwidth),
                         aligny * (self.height - newheight),
                         alignx * (self.width - newwidth) + newwidth,
                         aligny * (self.height - newheight) + newheight))
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
        print(f"Resize image {token}")
        img = Image.open(img_filename)
        cropped = img.crop_to_aspect(size[0], size[1])
        cropped.thumbnail(size, Image.ANTIALIAS)
        cropped.save(img_resized)

#    def draw_current_incivilite(token)

    def generate(self, token):
        global memidx, memidy

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

        issues_url = f'{self.api_path}/get_issues.php?c={CATEGORY}'
        data = download_url(issues_url)
        jissues = json.loads(data)
        list_near = []
        for i in jissues:
            geopoint_search = geopy.Point(
                float(i['coordinates_lat']), float(i['coordinates_lon']))
            dist = geopy.distance.distance(geopoint_issue, geopoint_search).m
            if dist <= 500:
                list_near.append(i)

        list_issue = {"total": {}}
        for issue in list_near:
            self.download_and_resize_image(issue['token'])
            filename = f"/tmp/{issue['token']}.png"
            img = Image.open(filename)
            ratio = img.size[0] / img.size[1]

            if ratio not in list_issue['total']:
                list_issue[ratio] = []
                list_issue['total'][ratio] = 0

            list_issue[ratio].append(issue)
            list_issue['total'][ratio] += 1

        topratio = sorted(list_issue['total'].items(),
                          key=lambda item: item[1], reverse=True)
        ratioidx = topratio[0][0]

        count = len(list_issue[ratioidx])
        nblines = int(math.sqrt((count)))
        totalshow = count - (count % nblines)
        nbcols = int(totalshow / nblines)

        # Resize main picture
        imgsize = (int(APPROXWIDTH), int(APPROXHEIGHT))
        self.download_and_resize_image(token, imgsize)

        stepx = APPROXWIDTH/nbcols
        stepy = APPROXHEIGHT/nblines
        imgsize = (int(stepx), int(stepy))
        for issue in list_issue[ratioidx]:
            self.download_and_resize_image(issue['token'], imgsize)

        # Load pictures
        img_filename = f"/tmp/{token}_size_{int(APPROXWIDTH)}_{int(APPROXHEIGHT)}.png"
        background = Image.open(
            f"{self.dir}/background_v2.png").convert("RGBA")
        picture = Image.open(img_filename).convert("RGBA")
        smiley = Image.open(f"{self.dir}/smiley.png").convert("RGBA")
        result = background

        idx = 0
        for x in range(nbcols):
            for y in range(nblines):
                if list_issue[ratioidx][idx]['token'] == token:
                    memidx = x
                    memidy = y

                img_filename = f"/tmp/{list_issue[ratioidx][idx]['token']}_size_{int(stepx)}_{int(stepy)}.png"
                thumbnail = Image.open(img_filename)
                result.paste(
                    thumbnail, (int(MOSAICX + (x*stepx)), int(MOSAICY+(y*stepy))))

                idx += 1

        # Draw red rectangle
        d = ImageDraw.Draw(result)
        d.rectangle(
            ((MOSAICX-MOSAICSPACE, MOSAICY-MOSAICSPACE), (APPROXWIDTH+MOSAICX+MOSAICSPACE, APPROXHEIGHT+MOSAICY+MOSAICSPACE)), fill=None, outline=COLOR, width=8)

        # sys.exit()
        # data = downloadFile(f"{api}/get_issues.php?c=2")
        # issues = json.loads(data)
        # count = len(issues)
        # montant = count*135

        # Load pictures

        divisor = picture.size[1] / APPROXHEIGHT
        newidth = int(picture.size[0]/divisor)
        newheight = int(picture.size[1]/divisor)
        self.download_and_resize_image(token, (newidth, newheight))
        filename = f"/tmp/{token}_size_{newidth}_{newheight}.png"
        picture = Image.open(filename).convert("RGBA")
        smiley = Image.open(f"{self.dir}/smiley.png").convert("RGBA")
        result.paste(picture, (DELTAX, DELTAY))

        d.rectangle(
            ((DELTAX-MOSAICSPACE, DELTAY-MOSAICSPACE), (APPROXWIDTH+DELTAX+MOSAICSPACE, APPROXHEIGHT+DELTAY+MOSAICSPACE)), fill=None, outline=COLOR, width=8)

        # Add smiley
        swidth, sheight = smiley.size
        sratio = swidth / sheight
        swidth = int(newidth * .3)
        sheight = int(swidth / sratio)

        randx = random.randint(0, APPROXWIDTH-swidth)
        randy = random.randint(0, APPROXHEIGHT-sheight)
        smiley = smiley.resize((swidth, sheight))
        result.paste(smiley, (DELTAX + randx, DELTAY+randy), smiley)

        reducesmiley = smiley
        reducesmiley = reducesmiley.resize((
            int(swidth/nbcols), int(sheight/nblines)))
        result.paste(reducesmiley, (MOSAICX + int((stepx*memidx)),
                                    MOSAICY+int((stepy*memidy))), reducesmiley)
        print(memidx)
        print(memidy)

        print(swidth)
        print(swidth/nbcols)
        result.save("/tmp/result.png", format="png")
        sys.exit()

        # Draw text
        fnt = ImageFont.truetype(f'{self.dir}/Cantarell-Regular.otf', 40)
        d = ImageDraw.Draw(result)
        d.text((10, cheight-100),
               f"{count}eme incivilités,", font=fnt, fill=(228, 6, 19, 255))
        d.text((10, cheight-50),
               f"soit {montant} € de contravations", font=fnt, fill=(228, 6, 19, 255))

        d.text((10, cheight-100),
               f"{count}eme incivilités,", font=fnt, fill=(30, 61, 144, 255))
        d.text((10, cheight-50),
               f"soit {montant :7,.0f} € de contravations", font=fnt, fill=(30, 61, 144, 255))

        # Save image
        result.save("/tmp/result.png", format="png")
