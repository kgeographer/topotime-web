#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# rev 10 Nov 2013 kg
# calculate intersection, return id, %, label in descending order
import os, re, sys, math, codecs, pickle
from shapely.geometry import Polygon, MultiPolygon
from descartes.patch import PolygonPatch
from helper5 import toJul;
from jdcal import gcal2jd, jd2gcal
# ww2 1946-03-21 1946-06-20
# pleiades 1240-01-01 1301-12-31; pleiades 849-01-01 899-10-26
def parseQuery(args):
   global collection, query
   if args[1] in ('ww2', 'pleiades') and args[2] and args[3]:
      print args
      query = dates2poly([args[2], args[3]])
      # print type(query), query
      file = open('../data/ttout/'+args[1]+'.pickle','rb')
      collection = pickle.load(file)
   else:
      return """need a collection (ww2, pleiades) AND
      a date array, e.g. ['1946-03-21', '1946-06-20']"""
   
def dates2poly(query):
   # *** does not handle negative dates grrr
   print 'the query: ', query
   if type(query) == list:
      qstart=toJul(query[0],'','')/1000000; 
      qend=toJul(query[1],'','')/1000000
      qparr=[(qstart,0),(qstart,1),\
                     (qend,1),(qend,0),(qstart,0)]
      qpoly=Polygon(qparr)
      return qpoly
   else:
      print """needs 2 of [-]Y{1,7}-MM-DD in square brackets (years can be negative and big)"""
      
def ttIntersect(coll, q): # e.g. collShapes, qpoly
   counter=0; resultArray=[]
   for i in xrange(len(coll)):
      result = {};
      if coll[i]['shapes'].intersection(q).area > 0: 
         counter +=1
         result['id']=coll[i]['id']; 
         result['label']=coll[i]['label']
         result['area']=(coll[i]['shapes'].intersection(q).area/q.area)*100 
         resultArray.append(result)
   resultArray = sorted(resultArray, key=lambda k: k['area'], reverse=True)
   print str(counter) + ' match(es)'
   #for r in resultArray: print r['id'], r['area'], r['label']
   for r in resultArray: print(r['id'], "{0:.2f}".format(r['area'])+'%', r['label'])
   
parseQuery(sys.argv)
ttIntersect(collection,query)