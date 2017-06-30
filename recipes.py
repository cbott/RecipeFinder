try:
    # Python 3
    from tkinter import *
    import tkinter.messagebox as tkMessage
except ImportError:
    # Python 2
    from Tkinter import *
    import tkMessageBox as tkMessage

import pickle
import random

RECIPE_FILE = "stored_recipes.dat"

# Data structure:
# { "Recipe 1 Name" : { "Text" : "instructions..."} }

def keywords_in_string(keys, text):
    """takes a list of words and tells how many of them are in the string"""
    count = 0
    for word in keys:
        count+=(word in text)
    return count / len(keys)# = percentage that the search matches

def load_recipe_file():
    """Open the recipe data file and return the corresponding dictionary"""
    try:
        with open(RECIPE_FILE, "rb") as f:
            data = pickle.load(f)
        return data
    except IOError:
        return {}

def overwrite_file(new_data):
    with open(RECIPE_FILE, "wb") as f:
        pickle.dump(new_data, f)
    
class Application(Frame):
    """Recipe finder application window"""
    def __init__(self, master):
        #super(Application, self).__init__(master)
        Frame.__init__(self, master)
        self.grid()
        self.create_fields()
    def create_fields(self):
        """create application input fields"""
        #instructions
        Label(self, text="Search recipes by keyword/ingredient. Separate multiple keywords with commas:").grid(
            row=0, column=0, columnspan=6)
        #Keyword input field
        self.search_params = Text(self, width = 50, height= 3,
                                  wrap = WORD)
        self.search_params.grid(row=1, column=0, columnspan = 5, rowspan=2)
        self.search_params.bind("<Return>", self.search)
        #"search" button
        Button(self, text = "Search Recipes", command = self.search).grid(
            row = 1, column=5)
        #random recipe button
        Button(self, text = "Random Recipe", command = self.random).grid(
            row = 2, column=5)
        #Output Text
        Label(self, text="Search Results: Click a recipe name to open").grid(row=3, column=0, columnspan = 4)
        #create output Text field
        self.results = Text(self, width=50, height=10,wrap=WORD)
        self.results.grid(row = 4, column = 0, columnspan = 6)
        
        self.scroll = Scrollbar(self)
        self.scroll.config(command=self.results.yview)
        self.scroll.grid(row=4, column=5, sticky=NS)
        
        self.results.config(yscrollcommand=self.scroll.set)
        
        self.results.bind("<ButtonRelease-1>", self.open_on_click)
    def search(self, *args):
        """search for recipes with given keywords"""
        #retreive search keywords
        raw_params = self.search_params.get(0.0, END).lower()
        keywords = [x.strip() for x in raw_params.split(',')]

        ##search code
        recipes = load_recipe_file()

        #perform search    
        search_results = []
        for rec in recipes:
            text_to_search = rec + " " + recipes[rec]["Text"]
            #only include results that fit the search
            if keywords_in_string(keywords,text_to_search) == 1:
                search_results.append(rec)
        #display search results
        self.results.delete(0.0, END)
        if search_results:
            self.results.insert(0.0, "\n".join(search_results))
        else:
            self.results.insert(0.0, "No recipes found with specified ingredients")

    def random(self):
        """display a random recipe"""
        self.results.delete(0.0, END)
        options = load_recipe_file()
        if options:
            recipe = random.choice(list(options))
        else:
            recipe = "No recipes found"
        self.results.insert(0.0, "Random recipe:\n"+recipe)

    def open_on_click(self, *args):
        #text widget to operate on
        box = self.results
        #line number of the cursor
        line = str(box.index("insert").split(".")[0])
        #get text on that line
        clicked_line = box.get(line+".0", line+".end")
        
        #show the recipe card for the recipe that was clicked
        card = RecipeCard(self, clicked_line)

class AddWindow(Toplevel):
    """Window for adding a recipe to the database"""
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.master = master
        self.title("Add Recipe")
        self.grid()
        self.draw()
        self.resizable(False, False)

    def draw(self):
        Label(self, text="Recipe Name:").grid(row=0, column=0)
        self.recipe_name = Entry(self, width=25)
        self.recipe_name.grid(row=0,column=1, padx=10, pady = 5)
        Button(self, text="Add to recipe box", command=self.add).grid(
            row=5,column=0,columnspan=6)
        self.recipe_name.focus_set()

    def add(self):
        name = self._format(self.recipe_name.get()).lower()
        if name:
            #check that the recipe doesn't already exist
            existing_recipes = load_recipe_file()
            if name in existing_recipes:
                popup = tkMessage.showinfo("This recipe already exists",
                        "Another recipe with the same name already exists.\nTry searching for it and using the edit feature")
                self.focus_force()
            else:
                RecipeCard(self.master, name)
                self.destroy()
        else:
            popup = tkMessage.showwarning("No recipe name specified",
                                "Please enter a recipe name")
            self.focus_force()
    def _format(self, string):
        """format entries for putting into database"""
        return string.strip()

class RecipeCard(Toplevel):
    """Window for adding a recipe to the database"""
    def __init__(self, master, recipe):
        """takes recipe name, shows recipe card with all info"""
        Toplevel.__init__(self, master)

        self.recipe_name = recipe
        
        #self.resizable(0,0)
        self.bar = Menu(self)
        self.bar.add_command(label="Edit", command = self.edit, underline=0)
        self.bar.add_command(label="Delete this recipe", command = self.delete)
        self.config(menu = self.bar)
        self.bind("<Control-e>", lambda x: self.edit())
        self.bind("<Control-s>", lambda x: self.edit())

        self.load_recipe()

        self.focus_force()

    def load_recipe(self):
        """Load recipe and show contents in window"""
        if self.recipe_name == "":
            self.title("Error Loading Recipe")#set window title
            return
        self.title(self.recipe_name.title())

        self.header = Label(self, text=self.recipe_name.title(), font="arial 18", bg="#FFFFFF")
        self.header.pack(fill=X)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.textbox = Text(self, wrap=WORD, yscrollcommand=scrollbar.set, font="arial 14")

        scrollbar.config(command=self.textbox.yview)
        self.textbox.pack(fill=BOTH, expand=YES)

        self.full_recipe = load_recipe_file().get(self.recipe_name)
        if self.full_recipe is not None:
            # recipe opened for viewing/editing
            self.ingredients = self.full_recipe["Text"]
            self.textbox.insert(0.0, self.ingredients)
            self.set_view_mode()
        else:
            # recipe opened for first time (adding)
            self.ingredients = ""
            self.set_edit_mode()

    def set_edit_mode(self):
        # Allow editing of open recipe
        self.textbox.config(state = NORMAL)
        self.bar.entryconfig(1, label="Save")
        self.mode = "edit"

    def set_view_mode(self):
        # Make open recipe read only
        self.textbox.config(state = DISABLED)
        self.bar.entryconfig(1, label="Edit")
        self.mode = "view"

    def update(self):
        """redraw the card"""
        self.textbox.delete(0.0, END)
        self.load_recipe(self.recipe_name)

    def edit(self):
        if self.mode == "view":
            self.set_edit_mode()
        elif self.mode == "edit":
            # save changes and return to view mode
            all_recipes = load_recipe_file()
            text = self.textbox.get(0.0, END)
            if all_recipes.get(self.recipe_name) is None:
                # New recipe
                all_recipes[self.recipe_name] = {"Text":text}
            else:
                # Editing existing recipe
                all_recipes[self.recipe_name]["Text"] = text

            overwrite_file(all_recipes)
            self.set_view_mode()

    def delete(self):
        confirm = tkMessage.askokcancel("Delete?", "Are you sure you would like to delete this recipe?")
        if confirm:#user confirms delete
            all_recipes = load_recipe_file()
            del all_recipes[self.recipe_name] #delete the recipe
            overwrite_file(all_recipes)
            self.destroy()
        else: #user cancels the delete
            self.focus_force()

##run application
root = Tk()
root.title("Colin's Recipe Book")
app = Application(root)
#create add window
#add_recipe = AddWindow(app)
#add_recipe.withdraw()
#create menu bar
menu_bar = Menu(root)
menu_bar.add_command(label="New Recipe", command = lambda: AddWindow(root), underline=0)
root.bind("<Control-n>", lambda e: AddWindow(root))

root.config(menu=menu_bar)
root.focus_force()
# run
root.mainloop()
