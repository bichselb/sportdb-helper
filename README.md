# SportDB Helper

Helferscript für die Anwesenheitskontrolle auf https://www.sportdb.ch.

## Problem

Das wöchentliche führen der Anwesenheitskontrolle ist äusserst mühsam:

![alt text](images/empty-form.png)

## Lösung

SportDB Helper startet von einem Excelfile, dass die J+S-ID und wöchentliche Anwesenheit
aller Teilnehmer enthält (als Referenz, siehe [./data/reference.xls](./data/reference.xls)).

Aufgrund dieser Daten füllt SportDB Helper automatisch die Anwesenheitskontrolle aus.

## Verwendung

Um SportDB Helfer zu verwenden, brauchst du [docker](https://docs.docker.com/install/), `git` und `make`.
Die folgende Anleitung wurde für Linux konzipiert.

```
git clone git@github.com:bichselb/sportdb-helper.git
cd sportdb-helper
make
```