# -*- coding: utf-8 -*-
"""
Skript das automatisch eine Zeittabelle zur Angabe im Zeitnachweis mit versch. KTs generiert
Created on Fri Aug 14 13:52:11 2020

@author: Steffen Schaepe, RD-RL
"""

import calendar
import sys
import random

Feiertagliste = {
    2020: [(24,2),(10,4),(13,4),(21,5),( 1,6),(11,6)],
    2021: [(15,2),( 2,4),( 5,4),(13,5),(24,5),( 3,6)],
    2022: [(28,2),(15,4),(18,4),(26,5),( 6,6),(16,6)],
    2023: [(20,2),( 7,4),(10,4),(18,5),(29,5),( 8,6)],
    2024: [(12,2),(29,3),( 1,4),( 9,5),(20,5),(30,5)],
    2025: [( 3,3),(18,4),(21,4),(29,5),( 9,6),(19,6)],
    2026: [(16,2),( 3,4),( 6,4),(14,5),(25,5),( 4,6)],
    2027: [( 8,2),(26,3),(29,3),( 6,5),(17,5),(27,5)],
    2028: [(28,2),(14,4),(17,4),(25,5),( 5,6),(15,6)],
    2029: [(12,2),(30,3),( 2,4),(10,5),(21,5),(31,5)],
    2030: [( 4,3),(19,4),(22,4),(30,5),(10,6),(20,6)]
}
Brueckentagliste = {
    2020: [(22,5),(12,6),(28,12),(29,12),(30,12)],
    2021: [(14,5),( 4,6),(27,12),(28,12),(29,12),(30,12)],
    2022: [(27,5),(17,6),(31,10),(27,12),(28,12),(29,12),(30,12)],
    2023: [(19,5),( 9,6),( 2,10),(27,12),(28,12),(29,12)],
    2024: [(10,5),(31,5),( 4,10),(23,12),(27,12),(30,12)],
    2025: [( 2,5),(30,5),(20, 6),(29,12),(30,12 )],
    2026: [( 2,1),(15,5),( 5, 6),(28,12),(29,12),(30,12)],
    2027: [( 7,5),(28,5),(27,12),(28,12),(29,12),(30,12)],
    2028: [(26,5),(16,6),( 2,10),(27,12),(28,12),(29,12)],
    2029: [(30,4),(11,5),( 1, 6),( 2,11),(27,12),(28,12)],
    2030: [(31,5),(21,6),( 4,10),(23,12),(27,12),(30,12)]
}

def timetofloat(timestr):
    timestr.replace(',','.')
    if '.' in timestr:
        return (float(timestr))
    hm = timestr.split(':')
    return float(hm[0]) + float(hm[1])/60.

def isFrei(d,m,y):
    if d ==  1 and m ==  1: return True
    if d ==  1 and m ==  5: return True
    if d ==  3 and m == 10: return True
    if d ==  1 and m == 11: return True
    if d == 24 and m == 12: return True
    if d == 25 and m == 12: return True
    if d == 26 and m == 12: return True
    if d == 31 and m == 12: return True
    if (d,m) in Feiertagliste[y]: return True
    if (d,m) in Brueckentagliste[y]: return True
    return False

sigma = .5
cal= calendar.Calendar()

#Um welchen Monat geht es eigentlich?
month = int(input("Bitte Monat eingeben (als Zahl) "))
year = int(input("Bitte Jahr eingeben (vollständig) "))

#Bestimme die Arbeitstage dieses Montats
#Sammle alle Tage die nicht am Wochenende sind
workdays = []
for x in cal.itermonthdays2(year, month):
    if x[0] != 0 and x[1] < 5:
        workdays.append(x[0])
#Streiche Feier- und Brückentage
workdays = [item for item in workdays if not isFrei(item, month, year)]

#Template für formatierte Ausgabe
row_format ="{:>5}" * (len(workdays))
print ()
print ("In " + str(month) + '.' + str(year) +' gab es folgende Arbeitstage:')
print (row_format.format(*workdays)) 

#Abfrage von Urlaubs- und Gleittagen etc. und Anpassen der Liste
u = [int(item) for item in input("Bitte Tage eingeben, an denen nicht gearbeitet wurde (Urlaub, Gleittag, etc. mit Leerzeichen getrennt) ").split()]
workdays = [item for item in workdays if not item in u]

#Update Template
row_format ="{:>5}" * (len(workdays))

#Abfrage der regulären Arbeitszeit 
regwh = float(input("Bitte reguläre Arbeitszeit eingeben (als Dezimalwert, Standard: 7.8) ").replace(',','.') or '7.8')

#Jetzt brauchen wir eine Liste der Arbeitszeit je Tag
workhours = []

#Hier sind zwei Möglichkeiten vorgesehen: Die automatische Generierung einer zufälligen Stundenliste nach regulärer Arbeitszeit und Überstunden und die händische Eingabe der Arbeitszeit für jeden Tag
sw = ''
while sw != 'J' and sw != 'N':
    sw = input('Möchten Sie für jeden Tag die Arbeitszeit einzeln eingeben (J/N)? ').upper()

#Händische Eingabe
if sw == 'J':
    for day in workdays:
        workhours.append(float(input("Bitte Arbeitszeit eingeben für den "+str(day)+'.'+str(month)+'.'+str(year)+ ' (Standard ' + str(regwh) + 'h) ').replace(',','.') or '7.8'))
#Automatische Generierung
else:
    #Gleitzeit abfragen
    glzsa = timetofloat(input("Bitte Gleitzeitsaldo am Monatsanfang laut Zeitausweis eingeben (hh:mm, Standard 0:00) ") or '0:00')
    glzse = timetofloat(input("Bitte Gleitzeitsaldo am Monatsende laut Zeitausweis eingeben (hh:mm, Standard 0:00) ") or '0:00')

    totwh = glzse-glzsa+regwh*len(workdays)
    restwh = totwh
    # print (glzse, glzsa, glzse-glzsa, regwh*len(workdays), avwh, avwh*len(workdays))
    #Würfel für jeden Tag bis auf den letzten eine Arbeitszeit aus einer Gaussverteilung um die Durchschnittliche tägliche Arbeitszeit
    #Dabei wird die schon verwendete totale Zeit berücksichtigt um Ausreisser am Ende des Monats zu verhindern
    for i, days in enumerate(workdays[:-1]):
        wh = 11
        #Nicht mehr als 10 Stunden Arbeit bitte
        while wh > 10:
            wh = round(random.gauss(restwh/(len(workdays)-i), sigma),1)
        workhours.append(wh)
        restwh -= wh
    #Der letzte Tag bekommt die verbleibenden Stunden
    workhours.append(round(restwh,1))
    # print (totwh, sum(workhours))

# print (workdays)
# print (workhours)

#Kostenträger-Abfrage. Per Default werden alle KTs der neuen Zeitaufschreibung verwendet.
kts = input("Bitte Liste der Kostenträger eingeben (mit Leerzeichen getrennt, leere Eingabe für alle) ").split() or ['3025501', '3025502', '3025503', '3025504', '3025505', '3025515', '3025530']
#Kurze Eingaben werden zu reales RD KTs aufgeblasen
kts = ['302550' + kt if len(kt) == 1 else '30255' + kt if len(kt) == 2 else kt for kt in kts ]

#Liste der Arbeitsanteile je KT
frac = []
#Bookkeeping der eingegebenen Dezimalstellen zur korrekten Darstellung der automatisch berechneten Rests
maxdig = 0

#Abfrage der Arbeitsanteile für alle KTs
for kt in kts[:-1]: 
    t = input("Bitte nominellen Arbeitsanteil für Kostenträger " + str(kt) + " angeben (dezimal, Standard 0) ").replace(',','.') or '0'
    frac.append(float(t))
    if len(t.split(".")[-1]) > maxdig: maxdig = len(t.split(".")[-1])
    #Mehr als 100% Arbeitsleistung sind leider nicht zulässig
    if (sum(frac) > 1.0):
        print ('FEHLER: Summe der Arbeitsanteile ist größer als 1,0')
        sys.exit(-1)
    #Wenn wir schon 100% haben können wir auch aufhören
    if (sum(frac) == 1.0): break
#Wenn noch nicht alles verteilt ist bekommt der letzte KT den Rest
if (sum(frac) < 1.0):
    frac.append(round(1.0-sum(frac), maxdig))
    print("Nomineller Arbeitsanteil für Kostenträger " + str(kts[-1]) + ": " + str(frac[-1])) 
#Übrige KTs am Ende der Liste ohne Arbeitsanteil werden entfernt
elif (len(frac) < len(kts)): kts = kts[:len(frac)]

#KTs ohne Arbeitsanteil werden entfernt
kts = [kt for (kt, f) in zip(kts,frac) if f > 0]
frac = [item for item in frac if item > 0]
# print (kts, frac)
    
#Liste mit einer Liste von Arbeitsstunden je KT
kttimes = [[] for kt in kts]

#Jetzt geht die eigentliche Arbeit los: Wir loopen über alle Arbeitstage
for day, wh in enumerate(workhours):
    totlen = 0
    #Arbeitstage mit 0 Stunden Arbeitszeit werden ignoriert
    if wh == 0:
        for ktl in kttimes:
            ktl.append(0)
        continue
    #Für jeden KT bis auf den letzen werden Arbeitzeiten aus einem Gauss um den Idealwert gewürfelt
    for kti, ktl in enumerate(kttimes[:-1]):
        time = round(random.gauss(frac[kti]*wh, sigma),1)
        #Negative Zeiten gibt es nicht
        if time < 0: time = 0
        ktl.append(time)
        totlen += time
    #Der letzte KT bekommt den Rest der noch übrigen Zeit für den Tag
    kttimes[-1].append(round(wh-totlen,1))
    
#Und nun zur Ausgabe
totwh = sum(workhours)
print()
print('Arbeitstage\t',row_format.format(*workdays))
print('Arbeitszeit\t',row_format.format(*workhours))


worktime = []
for kti, ktl in enumerate(kttimes):
    print('KT '+kts[kti]+'\t', row_format.format(*ktl))
    worktime.append(sum(ktl))
print()
#Crosscheck dass auch alles richtig ist
print('Arbeitsanteil je KT')
for kti in range(len(kts)):
    print('KT ' + kts[kti], str(round(worktime[kti]/totwh*100,1))+'%')
