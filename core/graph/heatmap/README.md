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
vgtool issue list --scope 34_montpellier --filter-category 2 --filter-category 7 --filter-date "2019-01-01 00:00:00" "2019-11-1 00:00:00" --group-by weeknumber,hour  --group-function approved:count:count --sort-by weeknumber --export pivot.csv
vgtool graph heatmap generate --import pivot.csv --output pivot.png

vgtool issue list --scope 34_montpellier --filter-category 2 --filter-category 7 --filter-date "2019-01-01 00:00:00" "2019-11-1 00:00:00" --group-by addresse  --group-function approved:count:count --sort-by count --export pivot.csv
vgtool graph heatmap generate --import pivot.csv --output pivot.png

```
