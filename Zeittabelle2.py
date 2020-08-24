# -*- coding: utf-8 -*-
"""
Skript das automatisch eine Zeittabelle zur Angabe im Zeitnachweis mit versch. KTs generiert
Created on Fri Aug 14 13:52:11 2020

@author: Steffen Schaepe, RD-RL
"""

import sys
import random
from itertools import zip_longest, accumulate

session = {}
sigma = .5

def make_parser(fieldwidths):
    cuts = tuple(cut for cut in accumulate(abs(fw) for fw in fieldwidths))
    pads = tuple(fw < 0 for fw in fieldwidths) # bool values for padding fields
    flds = tuple(zip_longest(pads, (0,)+cuts, cuts))[:-1]  # ignore final one
    parse = lambda line: tuple(line[i:j] for pad, i, j in flds if not pad)
    # optional informational function attributes
    parse.size = sum(abs(fw) for fw in fieldwidths)
    parse.fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
                                                for fw in fieldwidths)
    return parse

def filterZeitausweis(infile):
    fieldwidths = (2, -1, 2, -4, 4, -1, 5, -1, 5, -1, 5, -1, 5, -1, 5, -1, 5, -1, 6, -1, 3, -1, 5, -1, 3, -1, 5, -1, 3, -1, 5)  # negative widths represent ignored padding fields
    parse = make_parser(fieldwidths)
    outdata = []
    countseps = 0
    for line in infile:
        if line.startswith('---'):
            countseps += 1
            continue
        if countseps == 3:
            outdata.append(parse(line))
        if countseps > 3:
            break;
    return outdata
        
def timetofloat(timestr):
    sign = 1.
    if timestr.startswith('-'):
        sign = -1.
        timestr = timestr[1:]
    timestr = timestr.replace('.',':')
    if ',' in timestr:
        return (float(timestr.replace(',','.')))
    hm = timestr.split(':')
    return float(hm[0]) + float(hm[1])/60.

def calculatewhcorr(modifiers):
    corr = 0.0
    away = 0.0
    lmod = []
    for i in range(len(modifiers)-1):
        lmod.append((modifiers[i],modifiers[i+1]))
        i += 2
    for mod in lmod:
        if mod[0] == '':
            continue
        elif mod[1] == '':
            continue
        elif mod[0] == 'BA':
            away += timetofloat(mod[1])
        elif mod[0] == 'KR':
            away += timetofloat(mod[1])
        elif mod[0] == 'URL':
            away += timetofloat(mod[1])
        elif mod[0] == 'MP':
            corr -= timetofloat(mod[1])
        elif mod[0] == 'MXA':
            corr -= timetofloat(mod[1])
        elif mod[0] == 'RZ':
            corr -= timetofloat(mod[1])
        elif mod[0] == 'GZ+':
            corr += timetofloat(mod[1])
        elif mod[0] == 'GR':
            corr += timetofloat(mod[1])
        elif mod[0] == 'GA':
            corr += timetofloat(mod[1])
    return (corr, away)
            
def parseZeitausweis(input_filename):
    with open(input_filename, "r") as input_file:
        if 'workdays' not in session:
            session['workdays'] = []
        if 'workhours' not in session:
            session['workhours'] = []
        if 'awayhours' not in session:
            session['awayhours'] = []
        data = filterZeitausweis(input_file)
        #Wochenenden entfernen
        data = [item for item in data if not 'S' in item[0]]
        #Urlaube entfernen
        data = [item for item in data if not (item[10] == 'URL' and item[11] == '     ')]
        for i, line in enumerate(data):
            if line[0] == '  ':
                data[i-1] += line[10:]
        data = [item for item in data if not item[0] == '  ']
     
        
        for line in data:
            session['workdays'].append(line[0])
            timemod = calculatewhcorr(line[10:])
            session['workhours'].append(round(timetofloat(line[8]) + timemod[0],1))
            session['awayhours'].append(timemod[1])
    return

def cleanKTs():
    #print (session['kts'])
    #Kurze Eingaben werden zu reales RD KTs aufgeblasen
    session['kts'] = ['302550' + kt if len(kt) == 1 else '30255' + kt if len(kt) == 2 else kt for kt in session['kts'] ]
    #KTs ohne Arbeitsanteil werden entfernt
    session['kts'] = [kt for (kt, f) in zip(session['kts'],session['frac']) if f > 0]
    session['frac'] = [item for item in session['frac'] if item > 0]
    #Übrige KTs am Ende der Liste ohne Arbeitsanteil werden entfernt
    if (len(session['frac']) < len(session['kts'])): session['kts'] = session['kts'][:len(session['frac'])]
    # print (session['kts'], session['frac'])    
    return

def getFracs():
    if 'frac' not in session:
        session['frac'] = []    #Bookkeeping der eingegebenen Dezimalstellen zur korrekten Darstellung der automatisch berechneten Rests
    maxdig = 0
    
    #Abfrage der Arbeitsanteile für alle KTs
    for kt in session['kts'][:-1]: 
        t = input("Bitte nominellen Arbeitsanteil für Kostenträger " + str(kt) + " angeben (dezimal, Standard 0) ").replace(',','.') or '0'
        session['frac'].append(float(t))
        if len(t.split(".")[-1]) > maxdig: maxdig = len(t.split(".")[-1])
        #Mehr als 100% Arbeitsleistung sind leider nicht zulässig
        if (sum(session['frac']) > 1.0):
            print ('FEHLER: Summe der Arbeitsanteile ist größer als 1,0')
            sys.exit(-1)
        #Wenn wir schon 100% haben können wir auch aufhören
        if (sum(session['frac']) == 1.0): break
    #Wenn noch nicht alles verteilt ist bekommt der letzte KT den Rest
    if (sum(session['frac']) < 1.0):
        session['frac'].append(round(1.0-sum(session['frac']), maxdig))
        print("Nomineller Arbeitsanteil für Kostenträger " + str(session['kts'][-1]) + ": " + str(session['frac'][-1])) 
    return    

def computeTable():
    #print (session['kts'], session['frac'])
    #Liste mit einer Liste von Arbeitsstunden je KT
    if 'kttimes' not in session:
        session['kttimes'] = [[] for i in range(len(session['kts']))]    #Bookkeeping der eingegebenen Dezimalstellen zur korrekten Darstellung der automatisch berechneten Rests

    
    #Jetzt geht die eigentliche Arbeit los: Wir loopen über alle Arbeitstage
    for day, wh in enumerate(session['workhours']):
        totlen = 0
        #Arbeitstage mit 0 Stunden Arbeitszeit werden ignoriert
        if wh == 0:
            for ktl in session['kttimes']:
                ktl.append(0)
            continue
        #Für jeden KT bis auf den letzen werden Arbeitzeiten aus einem Gauss um den Idealwert gewürfelt
        for kti, ktl in enumerate(session['kttimes'][:-1]):
            time = round(random.gauss(session['frac'][kti]*wh, sigma),1)
            #Negative Zeiten gibt es nicht
            if time < 0: time = 0
            ktl.append(time)
            totlen += time
        #Der letzte KT bekommt den Rest der noch übrigen Zeit für den Tag
        session['kttimes'][-1].append(round(wh-totlen,1))
    return

def printTable():
    #Template für formatierte Ausgabe
    row_format ="{:>5}" * (len(session['workdays']))

    print()
    print('Arbeitstage\t',row_format.format(*session['workdays']))
    print('Arbeitszeit\t',row_format.format(*session['workhours']))
    print ('KT 0000009\t', row_format.format(*session['awayhours']))
    for kti, ktl in enumerate(session['kttimes']):
        print('KT '+session['kts'][kti]+'\t', row_format.format(*ktl))
    print()
    return

def printCrosscheck():
    totwh = sum(session['workhours'])
    worktime = []
    for ktl in session['kttimes']: worktime.append(sum(ktl))
    #Crosscheck dass auch alles richtig ist
    print('Arbeitsanteil je KT')
    for kti in range(len(session['kts'])):
        print('KT ' + session['kts'][kti], str(round(worktime[kti]/totwh*100,1))+'%')


input_filename = input("Bitte Dateiname des Zeitausweises angeben ")

parseZeitausweis(input_filename)

if 'kts' not in session:
    session['kts'] = []
#Kostenträger-Abfrage. Per Default werden alle KTs der neuen Zeitaufschreibung verwendet.
session['kts'] = input("Bitte Liste der Kostenträger eingeben (mit Leerzeichen getrennt, leere Eingabe für alle) ").split() or ['3025501', '3025502', '3025503', '3025504', '3025505', '3025515', '3025530']

getFracs()
# print ('1', session['kts'], session['frac'])    

cleanKTs()
# print ('2', session['kts'], session['frac'])    
   
computeTable()
# print ('3', session['kts'], session['frac'])    
    
#Und nun zur Ausgabe
printTable()
printCrosscheck()

