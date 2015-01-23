from tkinter import *
import tkinter.messagebox as tkMessage
import random

RECIPE_FILE = "recipes.txt"

def keywords_in_string(keys, text):
    """takes a list of words and tells how many of them are in the string"""
    count = 0
    for word in keys:
        count+=(word in text)
    return count / len(keys)# = percentage that the search matches

def read_recipe_file():
    """split file into list of recipes"""
    file = open(RECIPE_FILE, "r")
    all_results = file.read().lower()
    file.close()
    all_results = all_results.split("\n")
    return all_results
    
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
        #split by comma
        keywords = raw_params.split(",")
        #remove whitespace
        keyword_list = []
        for param in keywords:
            keyword_list.append(param.strip())

        ##search code
        recipes_searchable = self.compile_search_list()
        #perform search    
        search_results = []
        for rec in recipes_searchable:
            #only include results that fit the search
            if keywords_in_string(keyword_list,rec)==1:
                search_results.append(rec)
        #show just the names
        names = ""
        for res in search_results:
            names+=res.split("~")[0]+"\n"
        #display search results
        self.results.delete(0.0, END)
        if names:
            self.results.insert(0.0, names)
        else:
            self.results.insert(0.0, "No recipes found with specified ingredients")
    def random(self):
        """display a random recipe"""
        recipe = random.choice(self.compile_search_list())
        self.results.delete(0.0, END)
        self.results.insert(0.0, "Your random recipe:\n"+recipe.split("~")[0])
        
    def compile_search_list(self):
        """create a list of recipes name+ingredients"""
        recipes = read_recipe_file()
        #remove comments from items to be searched
        choices=[]
        for rec in recipes:
            choices.append(rec.split("`")[0])
        return choices
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
        self.title('Recipe Creator')
        self.grid()
        self.draw()
        self.minsize(200, 200)
        self.protocol('WM_DELETE_WINDOW', self.withdraw)

    def show(self):
        # Force to front
        self.withdraw()
        self.deiconify()

    def draw(self):
        #Recipe name
        Label(self, text="Name of recipe:").grid(row=0,column=0,sticky=W)
        self.recipe_name = Entry(self)
        self.recipe_name.grid(row=0,column=1)
        #Ingredients
        Label(self, text="Key ingredients:").grid(row=1,column=0,sticky=W)
        self.ingredients = Text(self, width=40,height=5,wrap=WORD)
        self.ingredients.grid(row=2,column=0,columnspan=6)
        #comments
        Label(self, text="Additional comments:").grid(row=3,column=0,sticky=W)
        self.comments = Text(self, width=30,height=4,wrap=WORD)
        self.comments.grid(row=4,column=0,columnspan=6)
        #add recipe
        Button(self, text="Add to recipe box", command=self.add).grid(
            row=5,column=0,columnspan=6)
    def add(self):
        name = self._format(self.recipe_name.get())
        ingredients = self._format(self.ingredients.get(0.0,END))
        comments = self._format(self.comments.get(0.0,END))
        if name:
            file = open(RECIPE_FILE, "a")
            data_to_write = "\n"+name+"~"+ingredients+"`"+comments
            file.write(data_to_write)
            file.close()
            self.recipe_name.delete("0",END)
            self.ingredients.delete(0.0,END)
            self.comments.delete(0.0,END)
            self.comments.insert(0.0, "Recipe added!")
        else:
            self.comments.insert(0.0, "Please fill in a recipe name")
    def _format(self, string):
        """format entries for putting into database"""
        return string.strip().replace("\n","-")
    
class EditWindow(Toplevel):
    """Window for editing a recipe already in the database"""
    def __init__(self, master, name, ingredients, comments):
        Toplevel.__init__(self, master)
        self.master = master

        self.name = name
        self.ingredients = ingredients
        self.comments = comments
        
        self.title('Recipe Editor')
        self.grid()
        self.draw()
        self.minsize(200, 200)
    def draw(self):
        #Recipe name
        Label(self, text="Name of recipe: " + self.name).grid(row=0,column=0,sticky=W)
        #Ingredients
        Label(self, text="Key ingredients:").grid(row=1,column=0,sticky=W)
        self.ingredients_field = Text(self, width=40,height=5,wrap=WORD)
        self.ingredients_field.grid(row=2,column=0,columnspan=6)
        self.ingredients_field.insert(0.0, self.ingredients)
        #comments
        Label(self, text="Additional comments:").grid(row=3,column=0,sticky=W)
        self.comments_field = Text(self, width=30,height=4,wrap=WORD)
        self.comments_field.grid(row=4,column=0,columnspan=6)
        self.comments_field.insert(0.0, self.comments)
        #edit button
        Button(self, text="Edit Recipe", command=self.overwrite).grid(
            row=5,column=0,columnspan=6)
    def overwrite(self):
        ing = self._format(self.ingredients_field.get(0.0,END))
        com = self._format(self.comments_field.get(0.0,END))
        data_to_write = self.name+"~"+ing+"`"+com

        all_recipes = read_recipe_file()
        for index, rec in enumerate(all_recipes):
            if rec.split("~")[0] == self.name:
                all_recipes[index] = data_to_write#replace current

        file = open(RECIPE_FILE, "w")
        sep = ""
        for rec in all_recipes:
            file.write(sep+rec)
            sep="\n"
        file.close()

        self.master.update()#re-draw the recipe card
        self.destroy()#close the editing window
        
    def _format(self, string):
        """format entries for putting into database"""
        return string.strip().replace("\n","-")
class RecipeCard(Toplevel):
    """Window for adding a recipe to the database"""
    def __init__(self, master, recipe):
        """takes recipe name, shows recipe card with all info"""
        Toplevel.__init__(self, master)

        self.requested_recipe = recipe
        
        self.grid()
        self.load_recipe(self.requested_recipe)
        self.resizable(0,0)
        self.bar = Menu(self)
        self.bar.add_command(label="Edit this recipe", command = self.edit)
        self.bar.add_command(label="Delete this recipe", command = self.delete)
        self.config(menu = self.bar)
        self.focus_force()
    def load_recipe(self, name):
        """given a recipe name, find all info for it"""
        self.full_recipe = "Error loading recipe~`"
        for rec in read_recipe_file():
            if self.requested_recipe == rec.split("~")[0]:
                self.full_recipe = rec
                break

        self.name = self.full_recipe.split("~")[0]
        self.ingredients = self.full_recipe.split("~")[1].split("`")[0]
        self.comments = self.full_recipe.split("`")[1]
        
        self.title(self.name.title())#set window title

        self.draw()
        
    def draw(self):
        """draw text and graphics for recipe card"""
        self.can = Canvas(self, width = 500, height = 300, bg="#F9F9F9")
        self.can.grid(row = 0, column=0)
        #draw card graphic
        self.can.create_line(0,38,500,38,fill = "red2", width=2.0)
        for y in range(63, 300, 25):
            self.can.create_line(0,y,500,y,fill = "blue2", width=2.0)
        #show text
        self.can.create_text(250,17, text=self.name.title(), font="arial 18")
        self.can.create_text(5,40, text="Ingredients:",
                             width=500, anchor = NW, font="arial 14")
        self.can.create_text(5,65, text=self.ingredients,
                             width=500, anchor = NW, font=("Comic Sans MS", 14))
        self.can.create_text(5,163, text="Comments:",
                             width=500, anchor = NW, font="arial 14")
        self.can.create_text(5,190, text=self.comments,
                             width=500, anchor = NW, font=("Comic Sans MS", 14))
    def update(self):
        """redraw the card"""
        self.can.delete("all")
        self.load_recipe(self.requested_recipe)
    def edit(self):
         self.editor = EditWindow(self, self.name, self.ingredients,
                                  self.comments)
    def delete(self):
        confirm = tkMessage.askokcancel("Delete this recipe?",
                                        "Are you sure you would like to delete this recipe?")
        if confirm:#user confirms delete
            all_recipes = read_recipe_file()
            for index, rec in enumerate(all_recipes):
                if rec == self.full_recipe:
                    del all_recipes[index]#delete the recipe

            file = open(RECIPE_FILE, "w")
            sep=""
            for rec in all_recipes:
                file.write(sep+rec)
                sep="\n"
            file.close()
            self.destroy()
        else:#user cancels the delete
            self.focus_force()
##run application
root = Tk()
root.title("Bott Family Recipe Finder")
app = Application(root)
#create add window
add_recipe = AddWindow(app)
add_recipe.withdraw()
#create menu bar
menu_bar = Menu(root)
menu_bar.add_command(label="Add Recipe", command = add_recipe.show)
root.config(menu=menu_bar)
root.focus_force()
#run
root.mainloop()
