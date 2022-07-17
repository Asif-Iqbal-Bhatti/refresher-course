######################################
## notebook_settings.py
##------------------------------------
## Goal: Provide css styling,
##        package and versions check,
##        notebook imports,
##        for jupyter notebooks
##------------------------------------
## Franck Iutzeler - 2017
######################################



#####################################
## Package and versions check
#####################################
import sys, importlib

def packageCheck(packageList):
	print(f'[Python version] \t{sys.version}\n\n[Packages versions]\n')
	for pack in packageList:
		try:
			try:
				mod = importlib.import_module(pack)
				print('{:20s}:\t{}'.format(pack,mod.__version__))
			except:
				mod = importlib.import_module(f"{pack}.info")
				print('{:20s}:\t{}'.format(pack,mod.version))
		except:
			print(f"{pack} has to be installed")


#####################################
## CSS restyling with style/style.css
#####################################
from IPython.core.display import HTML

def cssStyling():
    styles = open("./style/style.css", "r").read()
    return HTML(styles)




#####################################
## Notebook Importing
#####################################
import io, os, sys, types, nbformat

from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell

def find_notebook(fullname, path=None):
	"""find a notebook, given its fully qualified name and an optional path
    
    This turns "foo.bar" into "foo/bar.ipynb"
    and tries turning "Foo_Bar" into "Foo Bar" if Foo_Bar
    does not exist.
    """
	name = fullname.rsplit('.', 1)[-1]
	if not path:
	    path = ['']
	for d in path:
		nb_path = os.path.join(d, f"{name}.ipynb")
		if os.path.isfile(nb_path):
		    return nb_path
		# let import Notebook_Name find "Notebook Name.ipynb"
		nb_path = nb_path.replace("_", " ")
		if os.path.isfile(nb_path):
		    return nb_path
            

class NotebookLoader(object):
    """Module Loader for IPython Notebooks"""
    def __init__(self, path=None):
        self.shell = InteractiveShell.instance()
        self.path = path
    
    def load_module(self, fullname):
    	"""import a notebook as a module"""
    	path = find_notebook(fullname, self.path)

    	print(f"importing notebook from {path}")

    	# load the notebook object
    	nb = nbformat.read(path, as_version=4)


    	# create the module and add it to sys.modules
    	# if name in sys.modules:
    	#    return sys.modules[name]
    	mod = types.ModuleType(fullname)
    	mod.__file__ = path
    	mod.__loader__ = self
    	mod.__dict__['get_ipython'] = get_ipython
    	sys.modules[fullname] = mod

    	# extra work to ensure that magics that would affect the user_ns
    	# actually affect the notebook module's ns
    	save_user_ns = self.shell.user_ns
    	self.shell.user_ns = mod.__dict__

    	try:
    	  for cell in nb.cells:
    	    if cell.cell_type == 'code':
    	        # transform the input to executable Python
    	        code = self.shell.input_transformer_manager.transform_cell(cell.source)
    	        # run the code in themodule
    	        exec(code, mod.__dict__)
    	finally:
    	    self.shell.user_ns = save_user_ns
    	return mod




class NotebookFinder(object):
    """Module finder that locates IPython Notebooks"""
    def __init__(self):
        self.loaders = {}
    
    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return
        
        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)
        
        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]



sys.meta_path.append(NotebookFinder())

