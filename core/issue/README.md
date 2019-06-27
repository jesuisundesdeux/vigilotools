# Issue

## Help

### list

```
Usage: vgtool issue list [OPTIONS]

  Issues list

Options:
  -m, --max-distance INTEGER     max near distance
  -n, --filter-near [TOKEN]      Add token for searching near observations
  -d, --filter-date [START END]  Add timestamp filter. Ex: 2019-01-07
                                 2019-01-14
  -t, --filter-token TEXT        Add token filter
  -c, --filter-category TEXT     Add category filter
  -a, --filter-address TEXT      Add address filter
  --no-cache                     No cache remote issues file
  -f, --field TEXT               Show fields
  -l, --limit INTEGER            Limit issues  [default: -1]
  -s, --scope TEXT               Scope ID  [required]
  --help                         Show this message and exit.
```

### show

```
Usage: vgtool issue show [OPTIONS]

  Show scope informations

Options:
  -t, --token TEXT  Add token filter
  -n, --no-cache    No cache remote issues file
  -f, --field TEXT  Show fields
  -s, --scope TEXT  Scope ID  [required]
  --help            Show this message and exit.
```

### fields
```
Usage: vgtool issue fields [OPTIONS]

  Show available issue fields

Options:
  -s, --scope TEXT  [required]
  --help            Show this message and exit.
```

##Sample

### fields

```
vgtool issue fields --scope 34_montpellier

token
coordinates_lat
[...]
address
categorie
date
```

### list

```
vgtool issue list --scope 34_montpellier -f token -f token -f address -f categorie --limit 10

| token    | token    | address                                |   categorie |
|----------+----------+----------------------------------------+-------------|
| F1S85VYZ | F1S85VYZ | Rue du Pas du Loup, Montpellier        |           2 |
| FRQ78Y1X | FRQ78Y1X | Place Roger Salengro, Montpellier      |           2 |
| 49MFMY7Y | 49MFMY7Y | Place Bouschet de Bernard, Montpellier |           2 |
| CT01RM20 | CT01RM20 | Quai du Verdanson, Montpellier         |           2 |
| 0FFX1P97 | 0FFX1P97 | Quai du Verdanson, Montpellier         |           2 |
| ZS4GAF0S | ZS4GAF0S | Quai du Verdanson, Montpellier         |           2 |
| JN6IOIYF | JN6IOIYF | Avenue Émile Bertin-Sans, Montpellier  |           5 |
| 2J95Q3C1 | 2J95Q3C1 | Rue de Salaison, Montpellier           |           4 |
| AGYG5MCC | AGYG5MCC | Allée Louis Mazas, Montpellier         |           4 |
| 2JK724G7 | 2JK724G7 | Avenue du Docteur Pezet, Montpellier   |           9 |
```

```
vgtool issue list --scope 34_montpellier --filter-near YHOXPPN4 --max-distance 20 --filter-category 2

| token    | date       | address                     |   categorie |
|----------+------------+-----------------------------+-------------|
| E12C7548 | 2018-09-22 | Cours Gambetta, Montpellier |           2 |
| 058ED204 | 2018-09-29 | Cours Gambetta, Montpellier |           2 |
| ADAFDAFB | 2018-10-03 | Cours Gambetta, Montpellier |           2 |
| ADGC1M74 | 2019-03-16 | Cours Gambetta, Montpellier |           2 |
| 0AEO3KJR | 2019-03-16 | Cours Gambetta, Montpellier |           2 |
| S0NSEGH1 | 2019-03-24 | Cours Gambetta, Montpellier |           2 |
| JY4ZC0XC | 2019-03-25 | Cours Gambetta, Montpellier |           2 |
| 8KU167NX | 2019-04-19 | Cours Gambetta, Montpellier |           2 |
| Q0ELE8GV | 2019-04-20 | Cours Gambetta, Montpellier |           2 |
| 1NM72MU5 | 2019-04-24 | Cours Gambetta, Montpellier |           2 |
| CE7JQPHL | 2019-04-28 | Cours Gambetta, Montpellier |           2 |
| FA69C51C | 2019-05-08 | Cours Gambetta, Montpellier |           2 |

```
### show

```
vgtool issue show --scope 34_montpellier --token F1S85VYZ
          token : F1S85VYZ
coordinates_lat : 43.60007813184472
coordinates_lon : 3.8481921027445014
        address : Rue du Pas du Loup, Montpellier
        comment : stop la BC, pour aller discutailler au garage
    explanation :
           time : 08:23:00
         status : 0
          group : 0
      categorie : 2
       approved : 1
      timestamp : 1561357380
           date : 2019-06-24
```

## Sample

```
vgtool issue list --scope 34_montpellier -f address --filter-category 2 | tr '|' ' ' | sort | uniq -c | sort -rn | head -n 10

 181   Avenue de Lodève, Montpellier
  57   Cours Gambetta, Montpellier
  47   Rue de Barcelone, Montpellier
  43   Rue du Pas du Loup, Montpellier
  36   Route de Mende, Montpellier
  30   Avenue d'Assas, Montpellier
  27   Boulevard des Arceaux, Montpellier
  25   Avenue Bouisson Bertrand, Montpellier
  23   Rue Marioge, Montpellier
  23   Rue d'Alco, Montpellier
```
