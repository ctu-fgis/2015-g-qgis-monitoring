# Use pdb for debugging
#from PyQt4 import QtCore
#import pdb
# These lines allow you to set a breakpoint in the app
#pyqtRemoveInputHook()
#pdb.set_trace()

from qgis.core import *
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
import qgis.utils
import sys

class AeroGenParser():
    def __init__(self):
        self.areaXYZ={}
        self.tieLines={}
        self.surveyLines={}
        self.surveyLinesLatLon={}
#   http://intranet.geoecomar.ro/rchm/wp-content/uploads/downloads/2013/05/Agis-OM_VER2_2.3.2_.pdf
    def parseAreaXYZ(self,areaXYZfile):
        try:
            fp = open(areaXYZfile)
            lines=fp.readlines()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

        self.areaXYZ['L1'] = lines[0].split(';')[0]
        self.areaXYZ['L2'] = lines[1].split(';')[0]
        self.areaXYZ['L3'] = lines[2].split(';')[0]
        self.areaXYZ['L4'] = lines[3].split(';')[0]
        self.areaXYZ['L5'] = lines[4].split(';')[0]
        self.areaXYZ['L6'] = lines[5].split(';')[0]
        self.areaXYZ['Lat'] = lines[6].split(';')[0]
        self.areaXYZ['Lon'] = lines[7].split(';')[0]
        self.areaXYZ['CM'] = lines[8].split(';')[0]
        self.areaXYZ['dsx'] = lines[9].split(';')[0]
        self.areaXYZ['dsy'] = lines[10].split(';')[0]
        self.areaXYZ['dsz'] = lines[11].split(';')[0]
        self.areaXYZ['xSL'] = lines[12].split(';')[0]
        self.areaXYZ['ySL'] = lines[13].split(';')[0]
        self.areaXYZ['HSL'] = lines[14].split(';')[0]
        self.areaXYZ['spacingSL'] = lines[15].split(';')[0]
        self.areaXYZ['xTL'] = lines[16].split(';')[0]
        self.areaXYZ['yTL'] = lines[17].split(';')[0]
        self.areaXYZ['HTL'] = lines[18].split(';')[0]
        self.areaXYZ['spacingTL'] = lines[19].split(';')[0]
        self.areaXYZ['osffsetSL'] = lines[20].split(';')[0]
        self.areaXYZ['offsetTL'] = lines[21].split(';')[0]


        tieLines=[]
        currLine=23
        currLine1=23
        if lines[currLine][0] == 'c':
            for n in range(currLine,currLine+96):
                if lines[n][0] == 'c':
                    tieLines.append(lines[n])
                else:
                    currLine1=n
                    break
                currLine1=n
            self.areaXYZ['tieLines']=tieLines

        cornerPoints=[]
        currLine2=currLine1
        if lines[currLine1][0] == 'w':
            for n in range(currLine1,currLine1+16):
                if lines[n][0] == 'w':
                    cornerPoints.append(lines[n])
                else:
                    currLine2=n
                    break
                currLine2=n
            self.areaXYZ['cornerPoints']=cornerPoints


        wayPoints=[]
        if lines[currLine2][0] == 'l':
            for n in range(currLine2,currLine2+16):
                if lines[n][0] == 'l':
                    wayPoints.append(lines[n])
                else:
                    break
            self.areaXYZ['wayPoints']=wayPoints

        return self.areaXYZ

    def parseLines(self,linesFile, type='tieLines'):
        try:
            fp = open(linesFile)
            lines=fp.readlines()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        lineNum=2
        tieLines={}
        while True:
            if lines[lineNum].find('Line ')!=-1: #END HEADER, end footer
                lineId=lines[lineNum].split()[1]
                lineNum+=1
                line={}
                line['xcoor0']=lines[lineNum].split()[0]
                line['ycoor0']=lines[lineNum].split()[1]
                line['lon0']=lines[lineNum].split()[2]
                line['lat0']=lines[lineNum].split()[3]
                lineNum+=1
                line['xcoor1']=lines[lineNum].split()[0]
                line['ycoor1']=lines[lineNum].split()[1]
                line['lon1']=lines[lineNum].split()[2]
                line['lat1']=lines[lineNum].split()[3]
                tieLines[lineId]=line
            elif lines[lineNum+1].find('total distance') != -1 :
                break
            lineNum+=1
        if type == 'tieLines':
            self.tieLines=tieLines
        else:
            self.surveyLines=tieLines
        return tieLines

    def parseSurveyLines(self,surveyLinesFile):
        try:
            fp = open(surveyLinesFile)
            lines=fp.readlines()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise


        numOfLines=int(lines[0].split()[5])
        lineNum=3
        for i in range(0,numOfLines):
            line={}
            lineId=lines[lineNum].split()[0]
            line['lon0']=lines[lineNum].split()[1]
            line['lat0']=lines[lineNum].split()[2]
            lineNum+=1
            line['lon1']=lines[lineNum].split()[1]
            line['lat1']=lines[lineNum].split()[2]
            self.surveyLinesLatLon[lineId]=line

            lineNum+=1
        return self.surveyLinesLatLon



class AeroGenVectorBuilder():
    def __init__(self):
        pass

    def writeLayer(self,layer,filename="my_shapes.shp"):
        error = QgsVectorFileWriter.writeAsVectorFormat(layer, filename, "CP1250", None, "ESRI Shapefile")
        if error == QgsVectorFileWriter.NoError:
            return True
        else:
            return False

    def createArea(self,data,name):
        points=[]
        for line in data['tieLines']:
            ptline= line.split(';')
            points.append(QgsPoint(float(ptline[1]),float(ptline[2])))

        layer =  QgsVectorLayer('Polygon', name , "memory")

        poly = QgsFeature()
        poly.setGeometry(QgsGeometry.fromPolygon([points]))
        layer.dataProvider().addFeatures([poly])
        QgsMapLayerRegistry.instance().addMapLayers([layer])
        self.writeLayer(layer)


    def createLines(self,data,name):
        layer =  QgsVectorLayer('LineString', name , "memory")
        for key, value in data.iteritems():

            p1=QgsPoint(float(value['xcoor0']),float(value['ycoor0']))
            p2=QgsPoint(float(value['xcoor1']),float(value['ycoor1']))
            line = QgsFeature()
            line.setGeometry(QgsGeometry.fromPolyline([p1,p2]))

            layer.dataProvider().addFeatures([line])
            QgsMapLayerRegistry.instance().addMapLayers([layer])
            if self.writeLayer(layer):
                QgsMapLayerRegistry.instance().addMapLayer(layer)



def main():
    parser=AeroGenParser()
    poly= parser.parseAreaXYZ('/home/matt/Dropbox/CVUT/mgr/qgisPlugin/data/data_02_real_CR/area.xyz')
    tl=parser.parseLines('/home/matt/Dropbox/CVUT/mgr/qgisPlugin/data/data_02_real_CR/area_tl.xyz')
    sl=parser.parseLines('/home/matt/Dropbox/CVUT/mgr/qgisPlugin/data/data_02_real_CR/area_sl.xyz','x')
    #data4=parser.parseSurveyLines('/home/matt/Dropbox/CVUT/mgr/qgisPlugin/data/data_02_real_CR/area_sl_LatLon.xyz')


    vecBuilder=AeroGenVectorBuilder()
    vecBuilder.createLines(tl,'tl')
    vecBuilder.createArea(poly)
    vecBuilder.createLines(sl,'sl')
'''
main()
'''






















