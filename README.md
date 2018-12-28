# SportDB Helper

Helferscript für die Anwesenheitskontrolle auf https://www.sportdb.ch.

## Problem

Das wöchentliche führen der Anwesenheitskontrolle ist äusserst mühsam:

![](images/empty-form.png)

## Lösung

SportDB Helper startet von einem Excelfile, dass die J+S-ID und wöchentliche Anwesenheit
aller Teilnehmer enthält (als Referenz, siehe [./data/reference.xls](./data/reference.xls)).

Aufgrund dieser Daten füllt SportDB Helper automatisch die Anwesenheitskontrolle aus.

![](images/in-action.gif)

## Verwendung

### Anforderungen

Die folgenden Anforderungen sind für Ubuntu erklärt. Andere Systeme sollten analog verwendbar sein (nicht getestet).

Um SportDB Helfer zu verwenden, brauchst du [docker](https://docs.docker.com/install/), `git` und `make`:

- Um `git` und `make` installieren:
```
# for git
sudo apt-get install git-all
# for make
sudo apt-get install build-essential
# vnc client
sudo apt-get install tigervnc-viewer

```



- Docker auf Ubuntu installieren: https://docs.docker.com/install/linux/docker-ce/ubuntu/.

- Herunterladen von SportDB Helper:

```
git clone git@github.com:bichselb/sportdb-helper.git
cd sportdb-helper
```

### SportDB Helper

Um SportDB Helper laufen zu lassen:

```
./run --username "js-123456" --password "ABC" --course-id 1234567 --data-file ./data/attendance.xls
```

Für mehr Details zur Verwendung von SportDP Helper:
```
./run sportdb-helper --help
```