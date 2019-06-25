# Scope

## Help
```
Usage: vgtool scope [OPTIONS] COMMAND [ARGS]...

  Scopes informations

Options:
  --help  Show this message and exit.

Commands:
  list  Scopes list
  show  Show scope informations
```

##Sample

### list

```
vgtool scope list

| Scope ID             | Scope name                       |
|----------------------+----------------------------------|
| 13_aixmarseillemetro | Aix Marseille Provence Metropole |
| be_mons              | Belgique - Mons (beta)           |
| 29_brest             | Brest (beta)                     |
| 14_caen              | Caen (beta)                      |
| 72_lemans            | Le Mans (beta)                   |
| 57_metz              | Metz (beta)                      |
| 34_montpellier       | Montpellier                      |
| 91_parissaclay       | Paris-Saclay (beta)              |
| 76_rouen             | Rouen (beta)                     |
| 10_troyes            | Troyes Agglomération             |
| 92_valleesud         | Vallée Sud Grand Paris           |
| 00_test              | kentiss34 (uat)                  |
```
### show

```
vgtool scope show --scope 34_montpellier

╒════════════════╤══════════════╤═══════════╤═══════════╤════════════════════════════════════════╕
│ Scope ID       │ Scope name   │ Country   │ In prod   │ API                                    │
╞════════════════╪══════════════╪═══════════╪═══════════╪════════════════════════════════════════╡
│ 34_montpellier │ Montpellier  │ France    │ X         │ https://api-vigilo.jesuisundesdeux.org │
╘════════════════╧══════════════╧═══════════╧═══════════╧════════════════════════════════════════╛
```
