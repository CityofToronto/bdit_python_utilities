from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt.QtXml import QDomDocument

class IteratingMapper( object ):
    '''Holds settings for iterating over multiple congestion maps
    '''
    BACKGROUND_LAYERNAMES = []
    COMPOSER_LABELS = {}
    
    def __init__(self, logger, dbsettings, stylepath, templatepath, projectfile = None, console = False):
        self.logger = logger
        self.uri = self._new_uri(dbsettings)
        
        self.logger.info('Loading template')
        self.stylepath = stylepath
        self.template = QDomDocument()
        with open(templatepath, 'r') as templateFile:
            templateContent = templateFile.read()
            self.template.setContent(templateContent)
        
        self.project = None
        if projectfile:
            raise NotImplementedError('Loading projects causes Python to crash')
            self.logger.info('Loading project')
            self.project = QgsProject.instance()
            self.project.read(QFileInfo(projectfile))
        
        self.logger.info('Loading print composer')
        printcomposer = self._load_print_composer(console=console)
        self.composition = printcomposer['QgsComposition']
        self.map_settings = printcomposer['QgsMapSettings']
        self.composer_view = printcomposer['QgsComposerView']
        
        self.logger.info('Setting Map Registry and getting background layers')
        self.map_registry = QgsMapLayerRegistry.instance()
        self.background_layers = self.get_background_layers()
        self.layer = None
        self.logger.info('Mapper created successfully')
    
    def _new_uri(self, dbset):
        '''Create a new URI based on the database settings and return it

        Args:
            dbset: dictionary of database connection settings

        Returns:
            PyQGIS uri object'''
        uri = QgsDataSourceURI()
        uri.setConnection(dbset['host'], "5432", dbset['database'], dbset['user'], dbset['password'])
        return uri

    def _load_print_composer(self, console=True, template = None, iface = None):
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
            #canvas = QgsMapCanvas()
            # Next three lines from http://kartoza.com/en/blog/how-to-create-a-qgis-pdf-report-with-a-few-lines-of-python/
            #bridge = QgsLayerTreeMapCanvasBridge(
            #    QgsProject.instance().layerTreeRoot(), canvas)
            #bridge.setCanvasLayers()
            #mapSettings = canvas.mapSettings()
            mapSettings = QgsMapSettings()
            composition = QgsComposition(mapSettings)
            composition.loadFromTemplate(template)
#            map_item = composition.getComposerItemById('map')
#            map_item.setMapCanvas(canvas)
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
    
    def print_map(self, printpath, filetype = 'png'):
        '''Print the map to the specified location
        
        Args:
            printpath: string path to print to
            filetype: ['png','pdf'] determines type of image to print
        Raises:
            NotImplementedError: If filetype is not supported
        '''
        
        self.composition.refreshItems()
        if filetype == 'png':
            image = self.composition.printPageAsRaster(0)
            image.save(printpath)
        elif filetype == 'pdf':
            self.composition.exportAsPDF(printpath)
        else:
            raise NotImplementError('{filetype} is not supported'.format(filetype=filetype))
    
    def clear_layer(self):
        self.map_registry.removeMapLayer(self.layer)
        self.layer = None
    
    def close_project(self):
        if self.project is not None:
            self.project.clear()
            self.project = None

    #TODO: Cleanup, not sure if actually needed
#    def set_composition_layers(self):
#        layerslist = [QgsMapCanvasLayer(self.layer)] + self.background_layers
#        map_item = composition.getComposerItemById('map')
#        map_item.