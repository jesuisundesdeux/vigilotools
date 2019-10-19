# Issue

## Help

### list

```
Usage: vgtool issue list [OPTIONS]

  Issues list

Options:
  --max-distance INTEGER          max near distance
  -p, --populate TEXT             populate columen during loading data [image]
  --reverse, --rs                 Reverse sorting
  --having, --gh TEXT             Select records by grouped records or counter
                                  records
  --group-function, --gf TEXT     group function
                                  columname:function[count,max,min,mean,%]
  --group-by, --gb TEXT           group by
  --sort-by, --sb TEXT            sort by field
  --filter-string, --fs TEXT      Add string for searching near observations
  --filter-near, --fn [TOKEN]     Add token for searching near observations
  --filter-date, --fd [START END]
                                  Add timestamp filter. Ex: 2019-01-07
                                  2019-01-14
  --filter-token, --ft TEXT       Add token filter
  --filter-category, --fc TEXT    Add category filter
  --filter-address, --fa TEXT     Add address filter
  -i, --ignore-token, --it TEXT   Ignore token
  --no-cache                      No cache remote issues file
  --exp, --export TEXT            Export CSV
  --imp, --import TEXT            Import CSV
  -v, --verbose                   Verbose mode
  -f, --fields TEXT               Show fields. [ALL] or fieldsname. ex:
                                  token,date,time,address  [default: ALL]
  -t, --tail INTEGER              tail  [default: 0]
  -h, --head INTEGER              head  [default: 0]
  -s, --scope TEXT                [Scope ID ...], use [ALL] for use all scopes
  --help                          Show this message and exit.
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
  -s, --scope TEXT  Scope ID  [required]
  --help            Show this message and exit.
```

##Sample

### fields

**Show available fields**
`vgtool issue fields --scope 34_montpellier`

```
address,api_path,approved,categorie,comment,contact,coordinates_lat,coordinates_lon,country,date,department,explanation,group,hour,img_dhash,month,name,prod,scopeid,status,time,timeofday,timeofdayidx,timestamp,version,weekday,weekdayidx,year
```

### list

**Show entries**
`vgtool issue list --scope 34_montpellier --fields token,date,time,address,comment --head 5`

```
| token    | date       | time   | address                                   | comment                                     |
|----------+------------+--------+-------------------------------------------+---------------------------------------------|
| 5CE34893 | 2019-10-18 | 21:54  | Avenue Émile Diacon, Montpellier          | ya plus de trottoir, va mourir sur route!   |
| FBB9433A | 2019-10-18 | 18:39  | Rue du Jeu de Mail des Abbés, Montpellier | Véhicule garé sur la piste cyclable         |
| 2799F247 | 2019-10-18 | 18:39  | Route de Lavérune, Montpellier            | sur bc et devant passage piéton             |
| C9EBAB16 | 2019-10-18 | 12:23  | Boulevard Pénélope, Montpellier           | pratiquement tous les jours, génant piétons |
| 9FEB4C14 | 2019-10-18 | 10:21  | Avenue de Lodève, Montpellier             | Avenue de Lodève toujours N°1 des GCUM      |
```

**Show near entries**
`vgtool issue list --scope 34_montpellier --max-distance 20 --filter-category 2 --filter-near ADAFDAFB --fields token,date,address,comment --head 5`

```
| token    | date       | address                     | comment                           |
|----------+------------+-----------------------------+-----------------------------------|
| 8459D6EB | 2019-09-16 | Cours Gambetta, Montpellier | sans commentaire                  |
| 131C0AB3 | 2019-09-13 | Cours Gambetta, Montpellier | blocage piste                     |
| 4C86567E | 2019-09-06 | Cours Gambetta, Montpellier | après une accalmie de trois jours |
| A5FD6DD0 | 2019-08-22 | Cours Gambetta, Montpellier | Comme tous les soirs !            |
| 1C60BF06 | 2019-08-19 | Cours Gambetta, Montpellier | le combo !                        |
```


**Count entries by scope**
`vgtool issue list --scope ALL --group-by scopeid --group-function approved:count:count --sort-by count --reverse`

```
| scopeid              |   count |
|----------------------+---------|
| 00_test              |    3171 |
| 92_valleesud         |    2927 |
| 44_nantesmetropole   |    2182 |
| 13_aixmarseillemetro |     577 |
| 34_montpellier       |     285 |
| 10_troyes            |     267 |
| 26_valence           |     220 |
| 91_parissaclay       |     105 |
| be_mons              |      46 |
| 80_amiens            |      30 |
| 29_brest             |      20 |
```

**search top address**
```
vgtool issue list --scope 34_montpellier --filter-category 2 --group-by address --group-function approved:count:count --sort-by count --reverse  --having 'count:>=10' --export top.csv --head 10
vgtool issue list --import top.csv --group-by address --group-function count:sum:nb_obs,nb_obs:%:% --sort-by nb_obs --reverse
```

```
| address                                  |   nb_obs |        % |
|------------------------------------------+----------+----------|
| Avenue de Lodève, Montpellier            |      228 | 29.2308  |
| Rue du Pas du Loup, Montpellier          |      113 | 14.4872  |
| Cours Gambetta, Montpellier              |       86 | 11.0256  |
| Route de Lavérune, Montpellier           |       72 |  9.23077 |
| Route de Mende, Montpellier              |       66 |  8.46154 |
| Rue de Barcelone, Montpellier            |       62 |  7.94872 |
| Quai du Verdanson, Montpellier           |       45 |  5.76923 |
| Avenue d'Assas, Montpellier              |       40 |  5.12821 |
| Avenue Bouisson Bertrand, Montpellier    |       34 |  4.35897 |
| Rue du Moulin des Sept Cans, Montpellier |       34 |  4.35897 |
```


**Count entries by scope and categories**
`vgtool issue list --scope ALL --group-by scopeid,categorie --group-function approved:count:count --sort-by scopeid,count --reverse --head 20`
```
| scopeid        |   categorie |   count |
|----------------+-------------+---------|
| be_mons        |           4 |       6 |
| be_mons        |           2 |       4 |
| be_mons        |           3 |       2 |
| be_mons        |           5 |       1 |
| be_mons        |           8 |       1 |
| 92_valleesud   |           2 |    2140 |
| 92_valleesud   |           7 |     483 |
| 92_valleesud   |           3 |      71 |
| 92_valleesud   |           4 |      52 |
| 92_valleesud   |           8 |      37 |
| 92_valleesud   |           6 |      26 |
| 92_valleesud   |           5 |      17 |
| 92_valleesud   |         100 |      13 |
| 92_valleesud   |           9 |       1 |
| 91_parissaclay |           2 |      18 |
| 91_parissaclay |           4 |      17 |
| 91_parissaclay |           3 |       8 |
| 91_parissaclay |           6 |       3 |
| 91_parissaclay |           7 |       3 |
| 91_parissaclay |           8 |       1 |

```
**Search duplicated pictures**
`vgtool issue list --scope 34_montpellier --populate image --group-by img_dhash --having 'approved:count:>1' --sort-by img_dhash --fields img_dhash,token,address --head 10`

```
| img_dhash                        | token    | address                               |
|----------------------------------+----------+---------------------------------------|
| 08277b3f0f27725a0b3f00e0f83f2500 | WJV6CXAE | Avenue du Père Soulas, Montpellier    |
| 08277b3f0f27725a0b3f00e0f83f2500 | AIHXWA9Z | Avenue du Père Soulas, Montpellier    |
| 1838606b47f391743f3820017ec20360 | ED1975F4 | Place Roger Salengro Montpellier      |
| 1838606b47f391743f3820017ec20360 | 38142403 | Rue Guillaume Pellicier, Montpellier  |
| 1e8b74e7f765c6e6001afb4df2e10080 | 53AC3439 | Avenue Raymond Dugrand, Lattes        |
| 1e8b74e7f765c6e6001afb4df2e10080 | 2CB918F0 | Avenue Raymond Dugrand, Lattes        |
| 273b32328e1df4fc0f3e3067de3efcf1 | EB2EE995 | Rue du Faubourg de Nîmes, Montpellier |
| 273b32328e1df4fc0f3e3067de3efcf1 | C3A4DE4F | Rue du Faubourg de Nîmes, Montpellier |
| 2c7951341c9b094cfc010307fcb00000 | BCWMZZ7K | Avenue Raymond Dugrand, Montpellier   |
| 2c7951341c9b094cfc010307fcb00000 | YTI5VTVF | Avenue Raymond Dugrand, Montpellier   |
```

**Show numbers duplicated images**
`vgtool issue list --scope 34_montpellier --populate image --group-by img_dhash --group-function approved:count:count --having 'count:>1' --sort-by count --reverse)`
```
| img_dhash                        |   count |
|----------------------------------+---------|
| 6075181c31148c6ccfc74080f73f1e64 |       3 |
| 2c7951341c9b094cfc010307fcb00000 |       3 |
| 2dcf431e072121356008c3f8181f0700 |       3 |
| 8dcd5d9e3246e0bc07184d9c301fcf20 |       2 |
| e4a686e5cccce2e07000020605080402 |       2 |
| cdc0c4939d3c6c6d20ff448280204202 |       2 |
| c8e96b4b496b6242beb8a380d1fb6b2f |       2 |
| bd3efaecdc3c7cfcc1fffe81983061c1 |       2 |
| 91b0bcecfb6eaf230f02a13ff0c89820 |       2 |
```

`vgtool issue list -s 34_montpellier -f coordinates_lat,coordinates_lon --filter-category 2 --head 10 | tail -n +3 | awk '{print "[" $2 "," $4 "],"}'`
```
[43.6101,3.86681],
[43.6018,3.85284],
[43.6017,3.85259],
[43.6151,3.88124],
[43.615,3.8812],
[43.616,3.88076],
[43.6124,3.84546],
[43.6062,3.8674],
[43.6066,3.8672],
[43.6057,3.87859],
```

### show

`vgtool issue show --scope 34_montpellier --token F1S85VYZ`

```
        address : Rue du Pas du Loup, Montpellier
       api_path : https://api-vigilo.jesuisundesdeux.org
       approved : 1
      categorie : 2
        comment : stop la BC, pour aller discutailler au garage
        contact : xxxx@gmail.com
coordinates_lat : 43.60007813184472
coordinates_lon : 3.848192102744501
        country : France
           date : 2019-06-24
     department : 0
    explanation : nan
          group : 0
           hour : 08:00
          month : June
       monthidx : 6
           name : Montpellier
           prod : True
        scopeid : 34_montpellier
         status : 0
           time : 08:23
      timeofday : matin
   timeofdayidx : 1
      timestamp : 1561357380.0
        version : 0.0.12
        weekday : Monday
     weekdayidx : 1
     weeknumber : 26
           year : 2019
```
