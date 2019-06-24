# Collage

**Help**
```
Usage: vgtool poster collage all [OPTIONS]

  Generate from all issues

Options:
  -d, --add-date [START END]      Add timestamp filter. Ex: 2019-01-07
                                  2019-01-14
  -t, --add-token TEXT            Add token filter
  -c, --add-category TEXT         Add category filter
  -a, --add-address TEXT          Add address filter
  -n, --no-cache                  No cache remote issues file
  --title-textsize, --ts INTEGER  Title text size  [default: 36]
  --title-color, --tc TEXT        Title text color. ex: #FFFFFF  [default:
                                  #FFFFFF]
  --title-background, --tb TEXT   Background title color. ex: #000000
                                  [default: #000000]
  --title-text, --tt TEXT         Title text  [default: ]
  --img-textsize, --is INTEGER    Img text size  [default: 16]
  --img-color, --ic TEXT          Text color image. ex: #FFFFFF  [default:
                                  #FFFFFF]
  --img-background, --ib TEXT     Background color image ex: #000000
                                  [default: ]
  --img-text, --it TEXT           Text for all images: Ex: "date: {datetime}"
                                  [default: ]
  --width, --iw INTEGER           Width output image  [default: 2048]
  -o, --output TEXT               Output filename  [default: /tmp/collage.jpg]
  -l, --limit INTEGER             Limit issues  [default: 100]
  -s, --scope TEXT                Scope ID  [required]
  --help                          Show this message and exit.
```

**Sample**
```
vgtool poster collage all \
--scope 34_montpellier \
--add-date 2019-01-01 2019-06-30 \
--add-address lodève \
--img-text "{date}" \
--title-text "Avenue de Lodève - 2019" --output lodeve.jpg
```
