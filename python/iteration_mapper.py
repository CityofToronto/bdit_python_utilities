from qgis.core import *

from qgis.PyQt.QtXml import QDomDocument
from qgis.gui import QgsMapCanvasLayer

class IteratingMapper( object ):
    '''Holds settings for iterating over multiple congestion maps
    '''
    BACKGROUND_LAYERNAMES = None
    COMPOSER_LABELS = None
    
    def __init__(self, logger, dbsettings, stylepath, templatepath, projectfile = None, console = False):
        self.logger = logger
        self.uri = _new_uri(dbsettings)

        self.stylepath = stylepath
        self.agg_level = agg_level
        self.template = QDomDocument()
        with open(templatepath, 'r') as templateFile:
            templateContent = templateFile.read()
            self.template.setContent(myTemplateContent)
        
        self.project = None
        if projectfile:
            self.project = QgsProject.instance().read(QFileInfo(project_path))
        
        printcomposer = self._load_print_composer(console=console)
        self.composition = printcomposer['QgsComposition']
        self.map_settings = printcomposer['QgsMapSettings']
        self.composer_view = printcomposer['QgsComposerView']
        
        self.map_registry = QgsMapLayerRegistry.instance()
        self.background_layers = self.get_background_layers()
        self.layer = None
    

    @staticmethod
    def _new_uri(dbset):
        '''Create a new URI based on the database settings and return it

        Args:
            dbset: dictionary of database connection settings

        Returns:
            PyQGIS uri object'''
        uri = QgsDataSourceURI()
        uri.setConnection(dbset['host'], "5432", dbset['database'], dbset['user'], dbset['password'])
        return uri

    def _load_print_composer(self, console=True, template = None):
        '''Load a print composer template from object template or template argument

        Args:
            template: QDomDocument object read from a file
            console: boolean if method is used in QGIS console

        Returns:
            composition: a QGSCompsition loaded from the provided template 
            composerView: a QgsComposerView loaded from the provided template 
                (QGIS Python Console only)
            mapSettings: a QgsMapSettings object associated with composition'''
        
        if template is None:
            template = self.template
        
        composerView = None

        if console:
            composerView = iface.createNewComposer()
            composerView.composition().loadFromTemplate(template)
            composition = composerView.composition()
            mapSettings = composition.mapSettings()
        else:
            canvas = QgsMapCanvas()
            # Next three lines from http://kartoza.com/en/blog/how-to-create-a-qgis-pdf-report-with-a-few-lines-of-python/
            bridge = QgsLayerTreeMapCanvasBridge(
                QgsProject.instance().layerTreeRoot(), canvas)
            bridge.setCanvasLayers()
            mapSettings = canvas.mapSettings()
            composition = QgsComposition(mapSettings)
            composition.loadFromTemplate(template)
            map_item = composition.getComposerItemById('map')
            map_item.setMapCanvas(canvas)
        return {'QgsComposition': composition,
                'QgsMapSettings': mapSettings,
                'QgsComposerView': composerView}
    
    def get_background_layers(self, layernamelist = BACKGROUND_LAYERNAMES):
        '''Return background layers'''

        layers = [self.map_registry.mapLayersByName(name)[0] for name in layernamelist]
        layerslist = [QgsMapCanvasLayer(layer) for layer in layers]
        return layerslist

    def update_labels(self, labels_dict = COMPOSER_LABELS, labels_update = None):
        '''Change the labels in the QgsComposition using a dictionary of update values

        Iterates over the keys (label ids) and values (strings to update) of the labels_dict
        Finds the corresponding element of the composition, and updates it based on keys and 
        values provided in labels_update.

        Args:
            composition: the QgsComposition
            labels_dict: dictionary of labels to change of form 
                {'label_id':'label_text to {update_section}'}
            labels_update: dictionary of values to update labels with
                format: {'update_section':'update_value'}
        Returns:
            None'''
        for label_id, label_text in labels_dict.items():
            self.composition.getComposerItemById(label_id).setText(label_text.format(**labels_update))