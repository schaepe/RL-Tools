# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:52:11 2020

@author: scha_su
"""

import calendar
import sys
import random

month = int(input("Bitte Monat eingeben (als Zahl) "))
year = int(input("Bitte Jahr eingeben (vollständig) "))

cal= calendar.Calendar()

workdays = []
for x in cal.itermonthdays2(year, month):
    if x[0] != 0 and x[1] < 5:
        workdays.append(x[0])
print()
print ("In " + str(month) + '.' + str(year) +' gab es folgende Arbeitstage:')
print (*workdays,sep='\t')        

regwh = float(input("Bitte reguläre Arbeitszeit eingeben (als Dezimalwert, Standard: 7.8) ").replace(',','.') or '7.8')
s = input("Bitte Tage eingeben, an denen nicht die reguläre Stundenzahl (" + str(regwh) +") gearbeitet wurde (mit Leerzeichen getrennt) ")
nonregdays = list(map(int, s.split()))

workhours = []
for day in workdays:
    if day in nonregdays: 
        wh = float(input("Bitte Arbeitszeit eingeben für den "+str(day)+'.'+str(month)+'.'+str(year)+ ' '))
        workhours.append(wh)
    else:
        workhours.append(regwh)
        
# print (workhours)

kts = input("Bitte Liste der Kostenträger eingeben (mit Leerzeichen getrennt) ").split() or ['3025502', '3025503', '3025504']
for kti in range(len(kts)):
    if len(kts[kti]) == 1:
        kts[kti] = '302550' + kts[kti]
    elif len(kts[kti]) == 2:
        kts[kti] = '30255' + kts[kti]
frac = []
maxdig = 0
for kt in kts[:-1]: 
    t = input("Bitte nominellen Arbeitsanteil für Kostenträger " + str(kt) + " angeben (dezimal) ").replace(',','.')
    frac.append(float(t))
    if len(t.split(".")[-1]) > maxdig: maxdig = len(t.split(".")[-1])
frac.append(round(1.0-sum(frac), maxdig))
print("Nomineller Arbeitsanteil für Kostenträger " + str(kts[-1]) + ": " + str(frac[-1])) 

# print (kts, frac)
    
sigma = .5

kttimes = []
for kt in kts:
    kttimes.append([])

for day in range(len(workhours)):
    totlen = 0
    if workhours[day] == 0:
        for kti in range(len(kts)):
            kttimes[kti].append(0)
        continue
    for kti in range(len(kts)-1):
        time = round(random.gauss(frac[kti]*workhours[day], sigma),1)
        if time < 0: time = 0
        kttimes[kti].append(time)
        totlen += kttimes[kti][day]
    kttimes[-1].append(round(workhours[day]-totlen,1))
    
totwh = sum(workhours)
print()
print('Arbeitstage',*workdays, sep='\t')
print('Arbeitszeit',*workhours, sep='\t')

worktime = []
for kti in range(len(kts)):
    print('KT '+kts[kti], *kttimes[kti], sep='\t')
    worktime.append(sum(kttimes[kti]))
print()
print('Arbeitsanteil je KT')
for kti in range(len(kts)):
    print('KT ' + kts[kti], str(round(worktime[kti]/totwh*100,1))+'%')
