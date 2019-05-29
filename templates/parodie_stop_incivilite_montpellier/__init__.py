import os
import json
import random
import urllib.request

from PIL import Image, ImageDraw, ImageFont

def downloadFile(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text

class TPLparodie_stop_incivilite_montpellier():
    def __init__(self):
        self.dir = os.path.dirname(__file__)

    def generate(self, api,filename):
        data = downloadFile(f"{api}/get_issues.php?c=2")
        issues = json.loads(data)
        count = len(issues)
        montant = count*135

        # Load pictures
        background = Image.open(f"{self.dir}/background.png").convert("RGBA")
        picture = Image.open(filename).convert("RGBA")
        smiley = Image.open(f"{self.dir}/smiley.png").convert("RGBA")
        result = background

        # Get image informations
        dstpicture = [620,0,1920,720]
        cposx = dstpicture[0]
        cposy = dstpicture[1]
        cwidth = dstpicture[2] - cposx
        cheight = dstpicture[3] - cposy
        iwidth = picture.size[0]
        iheight = picture.size[1]
        isportrait = iheight>iwidth
        ratio = iheight / float(cheight)

        # Resize picture
        if isportrait:
            rwidth = iwidth
            rheight = iheight
            if ratio>0:
                rwidth = int(iwidth/ratio)
                rheight = int(iheight/ratio)
                picture = picture.resize((rwidth,rheight))

        # Paste picture
        result.paste(picture,(cposx,cposy))

        # Add smiley
        swidth,sheight = smiley.size
        sratio = swidth / sheight
        swidth = int(iwidth * .3)
        sheight = int(swidth / sratio)

        sposx = random.randint(cposx,cposx+rwidth-swidth)
        sposy = random.randint(cposy,cposy+rheight-sheight)
        smiley = smiley.resize((swidth,sheight))
        result.paste(smiley,(sposx,sposy),smiley)

        # Crop image
        result = result.crop((0,0,cposx+rwidth,cposy+rheight))

        # Draw text
        fnt = ImageFont.truetype(f'{self.dir}/Cantarell-Regular.otf', 40)
        d = ImageDraw.Draw(result)
        # d.text((10,cheight-100), f"{count}eme incivilités,", font=fnt, fill=(228,6,19,255))
        # d.text((10,cheight-50), f"soit {montant} € de contravations", font=fnt, fill=(228,6,19,255))

        d.text((10,cheight-100), f"{count}eme incivilités,", font=fnt, fill=(30,61,144,255))
        d.text((10,cheight-50), f"soit {montant :7,.0f} € de contravations", font=fnt, fill=(30,61,144,255))


        # Save image
        result.save("test.png", format="png")
