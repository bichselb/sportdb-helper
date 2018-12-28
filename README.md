# SportDB Helper

Helferscript für die Anwesenheitskontrolle auf https://www.sportdb.ch.

## Problem

Das wöchentliche führen der Anwesenheitskontrolle ist äusserst mühsam:

![](images/empty-form.png)

## Lösung

SportDB Helper startet von einem Excelfile, dass die J+S-ID und die wöchentliche Anwesenheit
aller Teilnehmer enthält (als Referenz, siehe [./data/reference.xls](./data/reference.xls)).

Aufgrund dieser Daten füllt SportDB Helper automatisch die Anwesenheitskontrolle aus ([Video in besserer Auflösung](images/in-action.mp4?raw=true)).

![](images/in-action.gif)

## Verwendung

### Installation

Die folgende Installationsanleitung ist für Ubuntu gedacht. Andere Systeme sollten analog verwendbar sein (nicht getestet, Anpassung braucht Erfahrung).

Um SportDB Helfer zu verwenden, brauchst du [docker](https://docs.docker.com/install/), `git` und `make`:

- Um `git` und `make` zu installieren:
```
# for git
sudo apt-get install git-all
# for make
sudo apt-get install build-essential

```

- Docker auf Ubuntu installieren: https://docs.docker.com/install/linux/docker-ce/ubuntu/.

- Herunterladen von SportDB Helper:

```
git clone git@github.com:bichselb/sportdb-helper.git
cd sportdb-helper
```

- Installation von SportDP Helper:

```
make image
```

- (Optional) Cleanup nach Verwendung

```
make clean
```

### SportDB Helper

Um SportDB Helper laufen zu lassen:

```
./run.sh --username "js-123456" --password "ABC" --course-id 1234567 ./data/attendance.xls
```

Für mehr Details zur Verwendung von SportDP Helper:
```
./run.sh --help
```
