"""
***************************************************************************
    spatiallyorderpoints.py
    ---------------------
    Date                 : March 2025
    Author               : Grant Sabraw
***************************************************************************
"""
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsField,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsProcessingOutputVectorLayer,
                       QgsVectorLayerExporter,
                       QgsFeedback)
from PyQt5.QtCore import QVariant
from qgis import processing


class SpatiallyOrderPoints(QgsProcessingAlgorithm):
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SpatiallyOrderPoints()

    def name(self):
        return 'spatiallyorderpoints'

    def displayName(self):
        return self.tr('Spatially order points')

    def group(self):
        return self.tr('Custom')

    def groupId(self):
        return 'custom'

    def shortHelpString(self):
        return self.tr(
            """
            This algorithm calculates the relative position of each point based on proximity to the next closest point in the feature. Each point has a unique position, is only considered once, is stored in a newly created field, and is given a relative position to a user-defined starting feature ID.
            
            Example: pt_order = [2, 3, 4, 1]; assuming feature IDs are sorted in ascending order (1, 2, 3, 4) and point 4 was selected as the starting point, point 4 is closest to point 1 which is closest to point 2 which is closest to point 3. 
            
            Works well with the Points to path tool. 
            
            Input layer must not have overlapping points. 
            """
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                self.tr('Input point layer'),
                types=[QgsProcessing.TypeVectorPoint]
            )
        )
 
        self.addParameter(
            QgsProcessingParameterString(
                'FIELD_NAME', 
                'Name of field to store point positions', 
                multiLine=False, 
                defaultValue='pt_order'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
            'STARTING_ID', 
            'ID of starting point', 
            type=QgsProcessingParameterNumber.Integer, 
            minValue=0, 
            defaultValue=1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                'OUTPUT',
                self.tr('ordered_points')
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        input_feature = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        if input_feature.geometryType() != 0:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, input_feature)
            )
        
        starting_id = self.parameterAsInt(parameters, 'STARTING_ID', context)
        field_name = self.parameterAsString(parameters, 'FIELD_NAME', context)
        output_path = self.parameterAsOutputLayer(parameters, 'OUTPUT', context)
        
        if len(field_name) > 10:
            feedback.pushWarning("WARNING: field name > 10 characters")
        
        # Copy input feature
        output_layer = input_feature.clone()
            
        # Check if field_name exists, if not, add it
        if output_layer.fields().lookupField(field_name) == -1:
            feedback.pushInfo('Creating new field...')
            output_layer.startEditing()
            output_layer.dataProvider().addAttributes([QgsField(field_name, QVariant.Int)])
            output_layer.commitChanges()
            feedback.pushInfo('Field created')
        else:
            feedback.pushInfo('Field already exists')
            
        # Create variables
        field_index = output_layer.fields().lookupField(field_name)
        id_list = input_feature.allFeatureIds()
        id_sort = sorted(id_list)
        if not starting_id in id_list:
            feedback.reportError("ERROR: ID of starting point not found", True)
            return {}
        
        closest_id = starting_id
        feedback.pushInfo('Number of features: ' + str(len(id_list)))
        if len(id_list) <= 1:
            feedback.reportError("ERROR: need at least 2 features", True)
            return {}
        
        count = 1
        ordered_result = []
        
        # Find the nearest point to the starting point, then use that nearest point as the starting point for the next iteration and repeat until every point has been logged
        for id in id_sort:
            j = 1
            
            row = []
            geom1 = input_feature.getGeometry(closest_id)
            for id2 in input_feature.getFeatures(): # I am assuming the feature iterator is ordered by feature id, it seems like it is
                geom2 = id2.geometry()
                distance = geom1.distance(geom2)
                row.append(distance)
                
                if feedback.isCanceled():
                    break
                    return {}
            
            sorted_row = sorted(row)
            smallest = sorted_row[1] # select the second item because the first will always be itself
            
            # While nearest point has already been logged or nearest point is the first point and current point is not the last point
            while closest_id in ordered_result or (len(ordered_result) != 0 and closest_id == starting_id and (len(ordered_result) < len(id_list) - 1)):
                smallest = sorted_row[j]
                closest_id = id_sort[row.index(smallest)]
                j += 1

            closest_id = id_sort[row.index(smallest)]
            ordered_result.append(closest_id)
            
            progress = count / (len(id_sort)) * 100
            feedback.setProgress(progress)
            count += 1
            
            if feedback.isCanceled():
                break
                return {}
        
        # Shift the list over because the first point in ordered_result is never the starting_id
        while ordered_result.index(starting_id) != 0:
            ordered_result = [ordered_result[-1]] + ordered_result[:-1] # shift list to the right by one
          
        # Update attributes with point positions
        output_layer.startEditing()
        for id in id_sort:
            output_layer.changeAttributeValue(id, field_index, ordered_result.index(id))
            if feedback.isCanceled():
                break
                return {}
        
        output_layer.commitChanges()
        
        error = QgsVectorLayerExporter.exportLayer(output_layer, output_path, "ogr", input_feature.crs(), False)
        if error[0] != QgsVectorLayerExporter.NoError:
            raise QgsProcessingException(f"ERROR: Failed to export layer: {error[1]}")
        if feedback.isCanceled():
            return {}
            
        return {'OUTPUT': output_path}