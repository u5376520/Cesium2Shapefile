#import packages
import json
from osgeo import ogr, osr

#Read an existing CZML file
filename = 'availcap.czml'
with open(filename, 'r') as example:
    num_items = -1
    substation_list = []
    packets = json.loads(example.read())
    for packet in packets[1:num_items]:
        availcap_list = packet[u'properties'][u'availcapinfo'][u'value']
        zone = {'Name': None,
                'Network': None,
                'coordinate': None,
                'geom': ogr.Geometry(ogr.wkbPolygon)} #Define zone details

        #Find and save relevant data from the original file
        zone["Network"] = packet[u'properties'][u'Network']
        zone["Name"] = str(packet[u'name'])
        zone["coordinate"] = packet[u'polygon'][u'positions'][u'cartographicDegrees']
        for year_data in availcap_list:
            zone["cap" + str(year_data[u'Year'])] = str(year_data[u'Availcap'])


        #Create Shapefile Geometry
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for i in range(len(zone['coordinate']))[0::3]:
            point_x = zone['coordinate'][i]
            point_y = zone["coordinate"][i+1]
            #print point
            ring.AddPoint(point_x, point_y)
        zone['geom'].AddGeometry(ring)
        substation_list.append(zone)


#Define the details of output shapefile
dstProjection = osr.SpatialReference()
dstProjection.SetWellKnownGeogCS('WGS84')
driver = ogr.GetDriverByName('ESRI Shapefile')
dstFile = driver.CreateDataSource('DistributionZones.shp')
dstLayer = dstFile.CreateLayer('layer', dstProjection)

#Define the attribute fields for each feature
for key in zone.keys():
    if key != 'geom' and key != 'coordinate':
        field_defn = ogr.FieldDefn(key, ogr.OFTString )
        field_defn.SetWidth( 32 )
        dstLayer.CreateField(field_defn)
    else:
        pass

#Save each zone as a feature
for zone in substation_list:
    feature = ogr.Feature(dstLayer.GetLayerDefn())
    lyrDefn = dstLayer.GetLayerDefn()
    for i in range(lyrDefn.GetFieldCount()):
        field = lyrDefn.GetFieldDefn(i).GetName()
        #print field
        value = zone[field]
        #print value
        feature.SetField(field, value)
    feature.SetGeometry(zone['geom'])

    dstLayer.CreateFeature(feature)


    feature.Destroy()

dstFile.Destroy()
