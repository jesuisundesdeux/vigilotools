# Collage

**Help**
```
Usage: vgtool poster collage filter [OPTIONS]

  Generate from all issues

Options:
  -d, --filter-date [START END]   Add timestamp filter. Ex: 2019-01-07
                                  2019-01-14
  -t, --filter-token TEXT         Add token filter
  -c, --filter-category TEXT      Add category filter
  -a, --filter-address TEXT       Add address filter
  -n, --no-cache                  No cache remote issues file
  --title-textsize, --ts INTEGER  Title text size  [default: 36]
  --title-color, --tc TEXT        Title text color. ex: #FFFFFF  [default:
                                  #FFFFFF]
  --title-background, --tb TEXT   Background title color. ex: #000000
                                  [default: #000000]
  --title-text, --tt TEXT         Title text  [default: ]
  --img-textsize, --is INTEGER    Img text size  [default: 16]
  --img-textmargin, --im INTEGER  Img text margin  [default: 10]
  --img-text, --it TEXT           Text for all images: Ex: "date: {datetime}"
                                  [default: ]
  --img-color, --ic TEXT          Text color image. ex: #FFFFFF  [default:
                                  #FFFFFF]
  --img-background, --ib TEXT     Background color image ex: #000000
                                  [default: ]
  --width, --iw INTEGER           Width output image  [default: 2048]
  -o, --output TEXT               Output filename  [default: /tmp/collage.jpg]
  -l, --limit INTEGER             Limit issues  [default: 100]
  -s, --scope TEXT                Scope ID  [required]
  --help                          Show this message and exit.
```

**Sample**
```
vgtool poster collage filter \
--scope 34_montpellier \
--filter-date 2019-01-01 2019-06-30 \
--filter-address lodève \
--img-text "{date}" \
--title-text "Avenue de Lodève - 2019" --output lodeve.jpg
```

```
vgtool poster collage filter \
--scope 34_montpellier \
--filter-token 8B86608G \
--filter-token 6QB0MJS1 \
--filter-token MHIQ6O4K \
--filter-token Q5SNZQD9 \
--filter-token Q6EVDD63 \
--img-background "#000000" \
--img-textsize "26" \
--img-text "{date} {time}" \
--title-text "Place Saint Denis - 2019" --output saint-denis.jpg
```
