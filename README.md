# vigilotools

## Installation

```
make install
source .virtualenv/bin/activate
vgtool scope list
```

## Sample

```
vgtool poster collage all \
--scope 34_montpellier \
--add-date 2019-01-01 2019-06-30 \
--add-address lodève \
--img-text "{date}" \
--title-text "Avenue de Lodève - 2019" --output lodeve.jpg
```

## Plugins list

[scope](core/scope/README.md)

[poster collage](core/poster/collage/README.md)
