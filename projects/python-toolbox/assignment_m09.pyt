# =============================================================================
# File             : assignment_m09.pyt
#
# Current Author   : Grant Sabraw
#
# Previous Author  : None
#
# Contact Info     : gsabraw@my.bcit.ca
#
# Purpose          : To define a toolbox for ArcGIS Pro that creates a JSON settings file 
#                    for a map series and runs a report based on the settings.
#
# Dependencies     : arcpy, traceback, os.path, json
#
# MakeSettings Parameters:
#                    0 - Atlas feature class (Feature Class)
#                    1 - Atlas field (Field)
#                    2 - Atlas series layer (String)
#                    3 - Atlas prefix (String)
#                    4 - Atlas map frame (String)
#                    5 - Atlas title (String)
#
# RunReport Parameters:
#                    0 - Atlas value (String)
#                    1 - Atlas series (String)
#
# Limitations      : Intended for uses with pre-existing layout with same naming scheme.
#
# Modification Log :
#    --> Created 2025-06-10 (rh)
#    --> Updated 2025-06-18 (fl)
#
# =============================================================================
import arcpy as ap
import arcpy.mp as mp
import json as js
from os import path
# =============================================================
# Create settings file name and settings dictionary
# =============================================================
__settings_file_name__ = path.join(path.split(__file__)[0], 'settings.json')
__toolbox_settings__ = {}
# =============================================================
# Create variables for settings keys
# =============================================================
__key_atlas_feature_class__ = 'atlas_feature_class'
__key_atlas_field__ = 'atlas_field'
__key_atlas_values__ = 'atlas_values'
__key_atlas_series_layer__ = 'atlas_series_layer'
__key_atlas_series_prefix__ = 'atlas_prefix'
__key_atlas_mapframe__ = 'atlas_mapframe'
__key_atlas_title__ = 'atlas_title'
# =============================================================
# Set default values for atlas parameters
# =============================================================
__default_atlas_feature_class__ = 'park_vir.gdb\\park_pa_bc'
__default_atlas_field__ = 'PROTECTED_LANDS_NAME'
__default_atlas_series_layer__ = 'Series_data'
__default_atlas_series_prefix__ = 'Park'
__default_atlas_mapframe__ = 'Main'
__default_atlas_title__ = 'Title'


class Toolbox:
    def __init__(self):
        self.label = "Toolbox"
        self.alias = "toolbox"

        self.tools = [MakeSettings, RunReport]


class MakeSettings(object):
    def __init__(self):
        self.label = "Make settings file"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        # =============================================================
        # Atlas feature class
        # =============================================================
        AtlasFeatureClass = ap.Parameter(
                displayName="Atlas feature class",
                name="AtlasFeatureClass",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Input")
        AtlasFeatureClass.value = __default_atlas_feature_class__
        # =============================================================
        # Atlas field
        # =============================================================
        AtlasField = ap.Parameter(
                displayName="Atlas field",
                name="AtlasField",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        AtlasField.parameterDependencies = [AtlasFeatureClass.name]
        AtlasField.value = __default_atlas_field__
        # =============================================================
        # Atlas series layer
        # =============================================================
        AtlasSeriesLayer = ap.Parameter(
                displayName="Atlas series layer",
                name="AtlasSeriesLayer",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        AtlasSeriesLayer.value = __default_atlas_series_layer__
        # =============================================================
        # Atlas prefix
        # =============================================================
        AtlasPrefix = ap.Parameter(
                displayName="Atlas prefix",
                name="AtlasPrefix",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        AtlasPrefix.value = __default_atlas_series_prefix__
        # =============================================================
        # Atlas map frame
        # =============================================================
        AtlasMapFrame = ap.Parameter(
                displayName="Atlas map frame",
                name="AtlasMapFrame",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        AtlasMapFrame.value = __default_atlas_mapframe__
        # =============================================================
        # Atlas title
        # =============================================================
        AtlasTitle = ap.Parameter(
                displayName="Atlas title",
                name="AtlasTitle",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        AtlasTitle.value = __default_atlas_title__
        
        params = [AtlasFeatureClass,
                  AtlasField,
                  AtlasSeriesLayer,
                  AtlasPrefix,
                  AtlasMapFrame,
                  AtlasTitle]
        
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        # =============================================================
        # Create dictionary to hold settings
        # =============================================================
        settings = {'version': 3.0}
        # =============================================================
        # Update settings with parameters
        # =============================================================
        settings.update({ __key_atlas_feature_class__ : parameters[0].valueAsText})
        settings.update({ __key_atlas_field__ : parameters[1].valueAsText})
        settings.update({ __key_atlas_series_layer__ : parameters[2].valueAsText})
        settings.update({ __key_atlas_series_prefix__ : parameters[3].valueAsText})
        settings.update({ __key_atlas_mapframe__ : parameters[4].valueAsText})
        settings.update({ __key_atlas_title__ : parameters[5].valueAsText})
        # =============================================================
        # Update settings with unique field values
        # =============================================================
        value_list = []        
        with ap.da.SearchCursor(parameters[0].valueAsText, parameters[1].valueAsText) as cursor:
            for row in cursor:
                if not row[0] in value_list:
                    value_list.append(row[0])
        value_list.sort()
        
        settings.update({'atlas_values' : value_list})
        # =============================================================
        # Save settings to JSON file
        # =============================================================
        with open(__settings_file_name__, 'w') as settings_file:
            js.dump(settings, settings_file)

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

class RunReport(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Run Atlas Report"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        aprx = mp.ArcGISProject('current')
        # =============================================================
        # Open settings file and load settings
        # =============================================================
        with open(__settings_file_name__, 'r') as settings_file:
            __toolbox_settings__ = js.load(settings_file)
        # =============================================================
        # Atlas value parameter
        # =============================================================
        AtlasValue = ap.Parameter(
                displayName="Atlas value",
                name="AtlasValue",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        AtlasValue.filter.list = __toolbox_settings__[__key_atlas_values__]
        # =============================================================
        # Atlas series parameter
        # =============================================================
        AtlasSeries = ap.Parameter(
                    displayName="Atlas series",
                    name="AtlasSeries",
                    datatype="GPString",
                    parameterType="Required",
                    direction="Input")
        layout_list = aprx.listLayouts(f'{__toolbox_settings__[__key_atlas_series_prefix__]}*')
        AtlasSeries.filter.list = [lt.name for lt in layout_list]
        
        params = [AtlasValue, AtlasSeries]
        return params
        
    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return
    
    def execute(self, parameters, messages):
        aprx = mp.ArcGISProject('current')
        # =============================================================
        # Open settings file and load settings
        # =============================================================
        with open(__settings_file_name__, 'r') as settings_file:
            __toolbox_settings__ = js.load(settings_file)
        # =============================================================
        # Get parameters and settings
        # =============================================================
        park = parameters[0].valueAsText
        series = parameters[1].valueAsText

        field = __toolbox_settings__[__key_atlas_field__]
        fc = __toolbox_settings__[__key_atlas_feature_class__]
        # =============================================================
        # Check if park name has single quotes and change them to double
        # single quotes for SQL
        # =============================================================
        if '\'' in park:
            park_split = park.split("'")
            park_sql = park_split[0]
            for i in range(len(park_split)):
                if i != 0:
                    park_sql = f'{park_sql}\'\'{park_split[i]}'
            clause = f'{field} = \'{park_sql}\''
        else:
            clause = f'{field} = \'{park}\''
        # =============================================================
        # Find extent
        # =============================================================
        with ap.da.SearchCursor(fc, 
                                [field, 'SHAPE@'], 
                                clause) as cursor:
            for row in cursor:
                extent = row[1].extent
        # =============================================================
        # Set map frame extent and definition query
        # =============================================================
        layout = aprx.listLayouts(series)[0]
        map_frame = layout.listElements("MAPFRAME_ELEMENT", 
                                         __toolbox_settings__[__key_atlas_mapframe__])[0]
        map_frame.camera.setExtent(extent)
        series_layer = map_frame.map.listLayers(__toolbox_settings__[__key_atlas_series_layer__])[0]
        series_layer.definitionQuery = clause
        # =============================================================
        # Change layout title
        # =============================================================
        title = layout.listElements('TEXT_ELEMENT', 'Title')[0]
        title.text = f'{park}'
        # =============================================================
        # Export layout as PDF and remove any slashes from park name
        # =============================================================
        park_pdf = park
        if '/' in park:
            park_pdf = park_pdf.replace('/', '')
        pdfFileName = f'{aprx.homeFolder}\{series}_{park_pdf}.pdf'
        pdf = mp.CreateExportFormat('PDF', pdfFileName)
        layout.export(pdf)
        ap.AddMessage(f'Exported {map_frame.name} to {pdfFileName}')
        
        return
    
    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return    