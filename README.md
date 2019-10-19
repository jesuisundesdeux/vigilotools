# vigilotools

## Installation

```
make install
source .virtualenv/bin/activate
vgtool scope list
```

## Help command

**IPV6 issue** `echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6`

```
Usage: vgtool [OPTIONS] COMMAND [ARGS]...

  Vigilo command tools

Options:
  -d, --debug  For debugging
  --help       Show this message and exit.

Commands:
  issue   Issues informations
  poster  Poster generation
  scope   Scopes informations
```

## Sample

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

[more samples](core/issue/README.md)

## Plugins list

* [scope](core/scope/README.md)
* [issue](core/issue/README.md)
* [poster collage](core/poster/collage/README.md)
