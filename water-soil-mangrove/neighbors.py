from qgis.utils import iface
from PyQt5.QtCore import QVariant

# Replace the values below with values from your layer.
# For example, if your identifier field is called 'XYZ', then change the line
# below to _NAME_FIELD = 'XYZ'
#_NAME_FIELD = 'class'
# Replace the value below with the field name that you want to sum up.
# For example, if the # field that you want to sum up is called 'VALUES', then
# change the line below to _SUM_FIELD = 'VALUES'
_SUM_FIELD = 'FID'

# Names of the new fields to be added to the layer
#_NEW_NEIGHBORS_FIELD = 'CLASS_NEIGHBORS'
_NEW_SUM_FIELD = 'FID_NEIGHBORS'

layer = iface.activeLayer()

# Create 2 new fields in the layer that will hold the list of neighbors and sum
# of the chosen field.
layer.startEditing()
layer.dataProvider().addAttributes(
        [#QgsField(_NEW_NEIGHBORS_FIELD, QVariant.String),
         QgsField(_NEW_SUM_FIELD, QVariant.Int)])
layer.updateFields()
# Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}

# Build a spatial index
index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)

# Loop through all features and find features that touch each feature
for f in feature_dict.values():
    sumf = f[_SUM_FIELD]
    print('Working on %s' % sumf)
    geom = f.geometry()
    # Find all features that intersect the bounding box of the current feature.
    # We use spatial index to find the features intersecting the bounding box
    # of the current feature. This will narrow down the features that we need
    # to check neighboring features.
    intersecting_ids = index.intersects(geom.boundingBox())
    # Initalize neighbors list and sum
    #neighbors = []
    neighbors_sum = []
    for intersecting_id in intersecting_ids:
        # Look up the feature from the dictionary
        intersecting_f = feature_dict[intersecting_id]
        # For our purpose we consider a feature as 'neighbor' if it touches or
        # intersects a feature. We use the 'disjoint' predicate to satisfy
        # these conditions. So if a feature is not disjoint, it is a neighbor.
        if (f != intersecting_f and
            not intersecting_f.geometry().disjoint(geom)):
            #neighbors.append(intersecting_f[_NAME_FIELD])
            neighbors_sum.append(intersecting_f[_SUM_FIELD])
    #f[_NEW_NEIGHBORS_FIELD] = ','.join(neighbors)
    #neighbors_sum = [str(int) for int in neighbors_sum]
    print(neighbors_sum)
    #f[_NEW_SUM_FIELD] = neighbors_sum
    #neighbors_sum = neighbors_sum.insert(0, f[_SUM_FIELD])
    #print(f[_NEW_SUM_FIELD])
    neighbors_sum.insert(0, sumf)
    print(neighbors_sum)
    with open('/data/mangrove-data/Kathy/biomass_project/downsampling/lap_07-18_site1/water-soil-mangrove/nn_only.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow(neighbors_sum)

    # Update the layer with new attribute values.
    layer.updateFeature(f)

layer.commitChanges()
print('Processing complete.')