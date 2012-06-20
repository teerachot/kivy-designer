import kivy
kivy.require('1.0.9')

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, \
        NumericProperty, StringProperty, OptionProperty, \
        ReferenceListProperty, AliasProperty
from kivy.clock import Clock
import random
import weakref
from functools import partial
from state import Saver

Builder.load_string('''#:kivy 1.0.9
<MenuBar>:
    size:self.size
    
<MenuTreeView>:
    size_hint_y: None
    hide_root: True
    height: self.minimum_height
    
<Toggle1>:
    border:(1, 1, 1, 1)
    
''')

class MenuTreeView(TreeView):
    pass

class Toggle1(ToggleButton):
    pass

class TreeViewLabel1(TreeViewLabel):
    '''Custom TreeViewLabel style 1 : Used for menu items'''
    def __init__(self,**kwargs):
        super(TreeViewLabel1,self).__init__(**kwargs)
        self.odd_color = (0, 0, 0, 0.7)
        self.even_color = (0,0,0,1)
        self.bold = True

class MenuBar(BoxLayout):
    '''The structure of the menubar is as follows:
    MenuBar(BoxLayout-horizontal)
        *SingleMenuItem(BoxLayout-vertical)
            *ToggleButton
            *ScrollView
                *MenuTreeView
    '''
    def __init__(self,**kwargs):
        super(MenuBar,self).__init__(**kwargs)
        self.canvas_area = kwargs.get('canvas_area')
        print self.canvas_area
        #File Menu
        treeview_file = MenuTreeView()
        items = ["Open...", "Save", "Save As..", "Sync git repo", "Quit.."]
        for item in items:
            node = TreeViewLabel1(text=item)
            if item in ["Save","Save As.."]:
                node.bind(is_selected = self.save_state)
            treeview_file.add_node(node)
        #Edit menu
        treeview_edit = MenuTreeView()
        items = ["Undo", "Redo", "Cut", "Copy", "Paste"]
        for item in items:
            node = TreeViewLabel1(text=item)
            treeview_edit.add_node(node)
        #Program menu
        treeview_program = MenuTreeView()
        items = ["Run", "Pause", "Stop", "Stop All"]
        for item in items:
            node = TreeViewLabel1(text=item)
            treeview_program.add_node(node)
        self.add_menu_item("File", treeview_file)
        self.add_menu_item("Edit", treeview_edit)
        self.add_menu_item("Program", treeview_program)
        return 
    
    def save_state(self,*kwargs):
        a = Saver(self.canvas_area)
    
    def add_menu_item(self,item_name,treeview_object):
        #Create a button with the name 'item_name'
        item_button = Toggle1(text = item_name, pos = (0,self.top), \
                    group = "menu"+str(self), height = self.height, size_hint_y = None)
        # Create a ScrollView and add its treeview. This will
        # be our scrollable menu
        parent_scrollview = ScrollView()
        parent_scrollview.add_widget(treeview_object)
        single_menu_item = BoxLayout(orientation='vertical',size_hint_y = 1)
        #This 'single_menu_item' will be the container for a single menu.
        # It would consist of a toggle button and a scrollview
        item_button.bind(state=partial(self.__add_scrollview, item_button, \
                                       single_menu_item, parent_scrollview))
        #On click should give a function that adds our scrollview to the single_menu_list
        single_menu_item.add_widget(item_button)
        self.add_widget(single_menu_item)

    def __add_scrollview(self,*kwargs):
        '''Function to attach scrollview of a single menu'''
        item_button, menu_list, parent_scrollview, \
                    instance, state = kwargs
        children_list = list(menu_list.children)
        last_child = children_list[len(children_list)-1]
        if state=='down':
            menu_list.add_widget(parent_scrollview)
            self.space_siblings(menu_list.parent, menu_list, True)
            menu_list.parent.height = min(last_child.height +\
            parent_scrollview.children[0].height, menu_list.parent.parent.height)
        else:
            children_list = list(menu_list.children)
            las_child = children_list[len(children_list)-1]
            menu_list.clear_widgets()
            self.space_siblings(menu_list.parent, menu_list, False)
            menu_list.add_widget(last_child)
            menu_list.parent.height = last_child.height

    def space_siblings(self, obj, skip, add):
        for child in obj.children:
            #We shouldn't add the dummy widget to the opened menu
            if child is not skip:
                if add:
                    try:
                        child.add_widget(child.spacing_widg)
                    except AttributeError:
                        child.spacing_widg = Widget()
                        child.add_widget(child.spacing_widg)
                else:
                   child.remove_widget(child.spacing_widg)