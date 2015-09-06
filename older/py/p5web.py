#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# rev 29 Oct 2013 kg
import os, re, sys, math, codecs, pickle
print 'fubar as usual'
print "This is the name of the script: ", sys.argv[0]
print "Number of arguments: ", len(sys.argv)
print "The arguments are: " , str(sys.argv)
if len(sys.argv)>1:
   data = sys.argv[1]
else:
   data = 'pleiades' # pleiades dance ttspec ww2

from shapely.geometry import Polygon, MultiPolygon
from descartes.patch import PolygonPatch
import helper5
from helper5 import parseDate, toJul;
import simplejson as json
from jdcal import gcal2jd, jd2gcal
wd='/webs/topotime/'

global newSpans, newCollection;

fn=wd + 'data/' + data + '.json'
# in
file = codecs.open(fn,"r", "utf-8"); 
coll=file.read(); file.close();
# out filenamewrite1
fnw1='data/ttout/'+data+'_collection.json' # collection with julian dates, geometry
w1 = codecs.open(wd+fnw1,"w", "utf-8"); 

newCollection = json.loads(coll)

periods = newCollection['periods']; print periods;
atom = newCollection['projection']['atom']
# parse into new collection
if (atom == 'date'):
   newCollection['periods']=parseDate(periods)
   json.dump(newCollection,w1,indent=2, sort_keys=True)
   w1.close()
else:
   print 'atom is not date; that\'s all we can parse now'

# for rendering, calcs
fnw2='data/ttout/'+data+'_geom_raw.json' # a raw geometries object for pyplot
w2 = codecs.open(wd+fnw2,"w", "utf-8");
fnw3='data/ttout/'+data+'_geom_d3.json' # a labeled geometries object for d3
w3 = codecs.open(wd+fnw3,"w", "utf-8");
fnpickle='data/ttout/'+data+'.pickle' #
w4=codecs.open(wd+fnpickle,"w")
# for plotting

collGeomRaw = []; collGeomObj = []; collShapes = []
for per in newCollection['periods']:
   geomArrayRaw = []; geomObj = {}; 
   pointsArray = []; perGeom = {}
   for i in range(len(per['geom'])):
      pointPair={}; 
      pointPair['x']=per['geom'][i][0]
      pointPair['y']=per['geom'][i][1]
      pointsArray.append(pointPair)
      geomArrayRaw.append(per['geom'][i])
   perGeom['shapes']=Polygon(geomArrayRaw)
   perGeom['id']=per['id']; perGeom['label']=per['label']
   #if len(geomArrayRaw) <5:
      #print per['id'], geomArrayRaw
   geomObj['points'] = pointsArray
   geomObj['label'] = per['label']
   geomObj['id'] = per['id']
   collGeomRaw.append(geomArrayRaw)
   collGeomObj.append(geomObj)
   collShapes.append(perGeom)
w2.write(json.dumps(collGeomRaw))
w2.close()
#w3.write('ttPolys = ')
w3.write(json.dumps(sorted(collGeomObj,key=lambda k: k['points'][0]['x'])))
w3.close()
# pickle.dump(collGeomRaw,w4)
pickle.dump(collShapes,w4)
w4.close()

# make multipolygon for collection
allArray = []
for x in xrange(len(collGeomRaw)):
   allArray.append([collGeomRaw[x],[]])
multi1 = MultiPolygon(allArray)
# a query geometry  id27 = 6500 to 3800 BC
# -652652.5 <--> 333502.5
# qpoly=Polygon(collGeomRaw[26])

def toGreg(jul):
   foo=jul-2400000.5
   gval=jd2gcal((jul-foo),foo)
   return str(gval[0])+'-'+str(gval[1])+'-'+str(gval[2])

# have collShapes
def ttSummary(coll,mpoly,query): # e.g. collShapes, multi1, qpoly
   if type(query) == list:
      qstart=toJul(query[0],'','')/1000000; 
      qend=toJul(query[1],'','')/1000000
      qparr=[(qstart,0),(qstart,1),\
                     (qend,1),(qend,0),(qstart,0)]
      qpoly=Polygon(qparr)
   else: qpoly = query
   print str(len(coll))+ ' periods'
   start = mpoly.bounds[0]; end = mpoly.bounds[2]
   areaColl = mpoly.area
   areaQ = qpoly.area
   print 'gross area: '+str(mpoly.area)+'; start:'+\
         str(toGreg(start*1000000)), '; end:'+\
         str(toGreg(end*1000000))   
   qs=qpoly.bounds[0]; qe=qpoly.bounds[2]
   print 'query start, end: '+str(toGreg(qs*1000000)), \
         str(toGreg(qe*1000000))   
   print 'query span is: ~'+str("%.2f" % (areaQ/areaColl*100))+\
         '% of the collection'

def dates2poly(query):
   # *** does not handle negative dates grrr
   if type(query) == list:
      qstart=toJul(query[0],'','')/1000000; 
      qend=toJul(query[1],'','')/1000000
      qparr=[(qstart,0),(qstart,1),\
                     (qend,1),(qend,0),(qstart,0)]
      qpoly=Polygon(qparr)
      return qpoly
   else:
      print """needs 2 of [-]Y{1,7}-MM-DD 
      in square brackets (years can be negative and big"""

# calc intersection, return id, label
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
   print str(counter) + ' matches'
   #for r in resultArray: print r['id'], r['area'], r['label']
   for r in resultArray: print(r['id'], "{0:.2f}".format(r['area'])+'%', r['label'])
   #print("{0:.2f}".format(a))
# print("%.2f" % a)

# C-Group (Nubian) peoples, flourished from c. 2240 BC to c. 2150 BC
# qpoly=Polygon(collGeomRaw[35]) # pull one out of Pleiades
# qpoly=dates2poly(['1240-01-01', '1301-12-31'])
if data=='pleiades':
   query=['849-01-01', '899-10-26']
elif data == 'ww2':
   query=['1946-03-21', '1946-06-20']
if type(query) == list:
   qstart=toJul(query[0],'sDate','s')/1000000; 
   qend=toJul(query[1],'eDate','e')/1000000
   qparr=[(qstart,0),(qstart,1),\
                  (qend,1),(qend,0),(qstart,0)]
   qpoly=Polygon(qparr)
# make qpoly contingent
ttSummary(collShapes, multi1, qpoly)
ttIntersect(collShapes,qpoly)
## calc intersection for given span, return area only
#counter=0; result = []; 
#for i in xrange(len(multi1)):
   #if multi1[i].intersection(qpoly).area>0:
      #counter +=1; print i
      #result.append(span.intersection(qpoly).area)
#result=sorted(result, reverse=True)
#print str(counter) + ' matches'
#for r in result: print r   

#for span in multi1:
   ##print span.distance(qpoly)
   #print qpoly.distance(span.centroid)