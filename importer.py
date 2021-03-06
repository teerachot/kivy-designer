import kivy
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, \
        Translate, Rotate, Scale
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from functools import partial
import sys
from os.path import isdir
import inspect

Builder.load_string('''#:kivy 1.0.9
<ImportPopup>:
    orientation:'vertical'
    filechooser:filechooser
    FileChooserListView:
        id:filechooser
        dirselect:False
    BoxLayout:
        size_hint_y:0.2
        Button:
            text:"Import this file"
            on_release:root.select_file()
''')

class ImportPopup(BoxLayout):
    '''This class provides the 'content' field of the popup that is raised
    whenever a new file needs to be imported'''
    filechooser = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ImportPopup, self).__init__(**kwargs)
        self.popup = kwargs.get('popup')
        self.designer = kwargs.get('designer')
        self.importer = kwargs.get('importer')
        
    def select_file(self, *largs):
        filechooser = self.filechooser
        selected = filechooser.selection
        if selected:
            file = selected[0]
            self.importer.file = file
            self.designer.popup.dismiss()
    
class Importer():
    ''' Main class that is called from menubar.py when 'Load' is clicked.
    This class instantiates the popup, and fills the 'content' field of that popup
    with an ImportPopup instance'''
    file = None
    
    def __init__(self, designer,*largs):
        self.designer = designer
        #Popup to specify from where the .py file should be loaded.
        content = ImportPopup(importer = self, popup = self.designer.popup, designer = self.designer)
        self.designer.popup = Popup(title='Select location to load .py file from',
                  content=content,
                  size_hint=(None, None), size=(400, 400))
        self.designer.popup.open()
        self.designer.popup.bind(on_dismiss = self.import_file)
        
    def import_file(self, *kwargs):
        #For testing. Point this to your generated kv file
        self.designer.popup = None
        file_path = self.file
        #Change separator for non-unix systems
        file_name = file_path.split("/")[-1]
        file_headpath = file_path.split(file_name)[0]
        sys.path.append(file_headpath)
        #You dont want the '.py' ending when you import, so..
        imported_file = __import__(file_name[0:-3])
        for name, value in inspect.getmembers(imported_file):
            if inspect.isclass(value):
                module_name =  value.__module__
                if module_name == file_name[0:-3]:
                    temp_widget = value()
                    #todo : Offer warning that current widgets will be cleared
                    self.designer.canvas_area.clear_widgets()
                    self.designer.widget = None
                    self.designer.root_name = temp_widget.__class__.__name__
                    self.process_bindings(temp_widget)
                    self.designer.canvas_area.add_widget(temp_widget)
                    self.designer.widget_tree.refresh()
    
    def process_bindings(self, root):
        '''A recursive function to apply 'show_properties', 'drag' and 
        'layout-highlight' bindings.'''
        if isinstance(root, Layout):
            with root.canvas:
                Color(0.5, 0.5, 0.5, .5)
                Rectangle(pos = root.pos, size = root.size)
            root.bind(pos = self.designer.redraw_canvas,size = self.designer.redraw_canvas)
        root.bind(on_touch_move = self.designer.drag)
        for child in root.children:
            self.process_bindings(child)

        
       

