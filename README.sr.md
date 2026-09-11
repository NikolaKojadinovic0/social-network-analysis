# Sistem za analizu društvene mreže i preporuku korisnika

[English version](README.md)

Univerzitetski projekat iz predmeta **Algoritmi i strukture podataka**, izrađen tokom školske 2025/2026. godine na Fakultetu tehničkih nauka Univerziteta u Novom Sadu.

## Pregled

Ova Python konzolna aplikacija modeluje usmereni graf društvene mreže i omogućava istraživanje njegove strukture, pronalaženje korisnika, rangiranje uticaja, upravljanje vezama i generisanje personalizovanih preporuka korisnika.

Aplikacija radi nad tri priložena sintetička skupa podataka, a ključne strukture i algoritmi implementirani su bez dodatnih biblioteka.

## Glavne funkcionalnosti

- usmereni graf praćenja sa pravilima blokiranja;
- globalno rangiranje uticaja pomoću algoritma PageRank;
- pretraga korisničkih imena i biografija uz rangiranje relevantnosti;
- automatsko dovršavanje pomoću trie strukture;
- predlozi za pogrešno uneta imena pomoću Levenshtein rastojanja;
- BFS obilazak nivoa povezanosti;
- hibridne preporuke pomoću algoritma Personalized PageRank i Jaccard sličnosti;
- dodavanje korisnika i follow veza tokom rada;
- hronološka istorija veza nastalih u trenutnoj sesiji;
- merenje performansi nad sva tri skupa podataka.

## Skupovi podataka

| Skup | Korisnici | Follow veze | Blokiranja |
|---|---:|---:|---:|
| `small` | 1.000 | 80.693 | 20 |
| `medium` | 10.000 | 354.503 | 200 |
| `full` | 81.306 | 1.768.135 | 1.626 |

Priloženi profili i odnosi su sintetički i namenjeni isključivo izradi akademskog zadatka.

Svaki direktorijum unutar `data/` sadrži:

| Fajl | Format | Značenje |
|---|---|---|
| `users.txt` | `id\|username\|bio` | korisnički profili |
| `connections.txt` | `from_id\|to_id` | usmerene follow veze |
| `blocked.txt` | `blocker_id\|blocked_id` | usmereni odnosi blokiranja |

## Strukture podataka i algoritmi

| Oblast | Implementacija |
|---|---|
| Predstavljanje grafa | hash mape, skupovi izlaznih veza, liste ulaznih veza i mapa izlaznih stepena |
| Globalno rangiranje | iterativni PageRank sa faktorom prigušenja `0.85`, granicom `1e-6`, obradom visećih čvorova i warm start postupkom |
| Izbor najboljih rezultata | heap za PageRank, pretragu, autocomplete, predloge i preporuke |
| Pretraga korisničkog imena | hash mapa za tačno poklapanje, trie za prefikse i provera podniske |
| Pretraga biografije | invertovani indeks i računanje relevantnosti |
| Automatsko dovršavanje | sopstvena trie struktura, uz rangiranje prema PageRank-u |
| Predlozi ispravki | sopstvena implementacija Levenshtein rastojanja dinamičkim programiranjem sa dva reda |
| Nivoi povezanosti | BFS pomoću `deque` reda i skupa posećenih čvorova |
| Preporuke | sopstveni Personalized PageRank i Jaccard sličnost biografija |

Hibridni skor preporuke računa se formulom:

```text
alpha * Personalized PageRank + (1 - alpha) * Jaccard sličnost
```

Iz kandidata se isključuju izabrani korisnik, korisnici koje već prati i korisnici između kojih postoji blokiranje u bilo kom smeru.

## Zahtevi

- Preporučuje se Python 3.11 ili noviji.
- Dodatni paketi nisu potrebni jer projekat koristi samo standardnu Python biblioteku.

## Pokretanje aplikacije

Iz glavnog direktorijuma projekta pokrenuti:

```bash
python main.py
```

Na početku se bira skup podataka:

```text
1 - small
2 - medium
3 - full
```

Pritiskom na Enter bira se `small`. Unosom `x` unutar neke funkcionalnosti korisnik se vraća u glavni meni.

Skup `small` je pogodan za brze provere, `medium` za interaktivnu demonstraciju, a `full` za proveru performansi.

## Opcije konzolnog menija

| Opcija | Funkcionalnost |
|---:|---|
| 1 | pretraga prema korisničkom imenu |
| 2 | pretraga prema rečima iz biografije |
| 3 | prikaz najuticajnijih korisnika |
| 4 | dodavanje follow veze |
| 5 | prikaz istorije interakcija |
| 6 | automatsko dovršavanje korisničkog imena |
| 7 | generisanje hibridnih preporuka |
| 8 | prikaz BFS nivoa povezanosti |
| 9 | prikaz „Did you mean” predloga |
| 10 | dodavanje novog korisnika |
| 0 | izlazak |

## Organizacija projekta

| Putanja | Namena |
|---|---|
| `main.py` | izbor skupa podataka, učitavanje i pokretanje aplikacije |
| `console_app.py` | konzolni meni, obrada unosa i prikaz rezultata |
| `user.py` | model `User` i tokenizacija biografije |
| `interaction.py` | model `FollowInteraction` |
| `social_graph.py` | graf, PageRank, PPR, BFS, korisnici, veze i istorija |
| `trie.py` | sopstvena trie struktura i autocomplete |
| `search_engine.py` | pretraga, invertovani indeks i predlozi ispravki |
| `recommendation_engine.py` | Jaccard sličnost i hibridne preporuke |
| `benchmark.py` | reprezentativno merenje performansi |
| `tests/` | automatizovani jedinični i integracioni testovi |
| `data/` | priloženi skupovi `small`, `medium` i `full` |

## Automatizovani testovi

Iz glavnog direktorijuma pokrenuti:

```bash
python -m unittest discover -s tests -v
```

Ukupno 23 testa proveravaju učitavanje i izmene grafa, konvergenciju algoritama PageRank i Personalized PageRank, pravila blokiranja, istoriju interakcija, BFS, trie operacije, relevantnost pretrage, predloge ispravki, ažuriranje indeksa, filtriranje i rangiranje preporuka, kao i integraciju sa priloženim `small` skupom projekta.

## Benchmark

Benchmark se pokreće komandom:

```bash
python benchmark.py
```

Mere se učitavanje podataka, PageRank, formiranje indeksa, pretraga, autocomplete, predlozi ispravki, BFS, preporuke, izmene grafa, istorija i dinamičko ažuriranje indeksa. Benchmark služi za merenje performansi, dok automatizovani testovi proveravaju ispravnost.

Pokretanje nad `full` skupom može trajati nekoliko minuta jer obuhvata više PageRank i Personalized PageRank proračuna.

### Rezultati za full skup

Vrednosti predstavljaju prosek pet uzastopnih pokretanja na istom računaru uz Python 3.11.1 i Windows 11. Opseg prikazuje najmanje i najveće izmereno vreme.

| Operacija | Prosečno vreme | Izmereni opseg |
|---|---:|---:|
| Učitavanje ulaznih fajlova | 5,49 s | 5,11-6,06 s |
| Početni PageRank | 47,35 s | 45,33-48,03 s |
| Formiranje trie strukture | 2,97 s | 2,89-3,08 s |
| Formiranje invertovanog indeksa | 0,815 s | 0,795-0,850 s |
| Did you mean | 0,109 s | 0,106-0,112 s |
| BFS do nivoa 3 | 0,055 s | 0,051-0,058 s |
| Hibridne preporuke | 53,75 s | 50,66-58,34 s |
| Nova veza i warm-start PageRank | 4,25 s | 3,91-4,49 s |
| Novi korisnik i PageRank od početka | 48,97 s | 45,86-51,11 s |
| Ukupna početna inicijalizacija | 56,63 s | 54,61-57,68 s |
| PPR i dve izmene grafa | 106,98 s | 100,44-112,83 s |

Kompletno pokretanje `full` benchmarka trajalo je prosečno približno 2 minuta i 44 sekunde, uz raspon od oko 2:35 do 2:50. Uobičajene interaktivne operacije, kao što su pretraga korisničkog imena i biografije, izbor najbolje rangiranih korisnika i autocomplete, pojedinačno su završene za manje od 0,017 sekundi.

Svih pet pokretanja dalo je iste algoritamske rezultate: 81.306 korisnika i 1.768.135 veza, 58 PageRank iteracija, 59 Personalized PageRank iteracija, 504.027 trie čvorova, 148.143 jedinstvene indeksirane reči i 30.198 korisnika dostignutih BFS-om do nivoa 3.

Vremena zavise od hardvera, operativnog sistema, verzije Python-a i trenutnog opterećenja računara.

## Obim i ograničenja

- Korisnici i veze dodati kroz meni postoje samo tokom trenutnog pokretanja i ne upisuju se u ulazne fajlove.
- Istorija sadrži samo veze napravljene tokom trenutne sesije jer priložene veze nemaju vreme nastanka.
- Projekat je usmeren na grafovske algoritme, strukture podataka, pretragu i preporuke, a ne na izradu kompletne platforme društvene mreže.

## Akademski kontekst

Projekat je samostalno izrađen kao drugi projektni zadatak iz predmeta **Algoritmi i strukture podataka**. Cilj je bio praktična primena grafova, heširanja, heap i trie struktura, BFS-a, dinamičkog programiranja, indeksiranja i algoritama rangiranja nad većim skupom podataka.
