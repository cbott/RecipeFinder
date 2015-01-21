from tkinter import *
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
    return all_results.split("\n")
    
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
        Label(self, text="Search recipes by keyword/ingredient. Separate multiple items with commas:").grid(
            row=0, column=0, columnspan=6)
        #Keyword input field
        self.search_params = Text(self, width = 50, height= 3,
                                  wrap = WORD)
        self.search_params.grid(row=1, column=0, columnspan = 5, rowspan=2)
        #"search" button
        Button(self, text = "Search Recipes", command = self.search).grid(
            row = 1, column=5)
        #random recipe button
        Button(self, text = "Random Recipe!", command = self.random).grid(
            row = 2, column=5)
        #Output Text
        Label(self, text="Search Results:").grid(row=3, column=0)
        #create output Text field
        self.results = Text(self, width=50, height=10,wrap=WORD)
        self.results.grid(row = 4, column = 0, columnspan = 6)
        
        self.scroll = Scrollbar(self)
        self.scroll.config(command=self.results.yview)
        self.scroll.grid(row=4, column=5, sticky=NS)
        
        self.results.config(yscrollcommand=self.scroll.set)
        
        self.results.bind("<ButtonRelease-1>", self.open_on_click)
    def search(self):
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
        
        full_recipe = "Error loading recipe~`"
        for rec in read_recipe_file():
            if clicked_line in rec:
                full_recipe = rec
                break
        #show the recipe card for the recipe that was clicked
        card = RecipeCard(self, full_recipe)

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
        self.comments = Text(self, width=20,height=4,wrap=WORD)
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

class RecipeCard(Toplevel):
    """Window for adding a recipe to the database"""
    def __init__(self, master, recipe):
        Toplevel.__init__(self, master)
        
        self.recipe = recipe
        self.name = recipe.split("~")[0]
        self.ingredients = recipe.split("~")[1].split("`")[0]
        self.comments = recipe.split("`")[1]
        
        self.title(self.name)
        self.grid()
        self.draw()
        self.minsize(400, 200)
    def draw(self):
        #Label(self, text="Name of recipe: "+self.name).grid(row=0,column=0,sticky=W)
        #Label(self, text="Ingredients: "+self.ingredients).grid(row=1,column=0,sticky=W)
        #Label(self, text="Comments: "+self.comments).grid(row=2,column=0,sticky=W)
        self.can = Canvas(self, width = 500, height = 300, bg="white")
        self.can.grid(row = 0, column=0)
        #draw card graphic
        self.can.create_line(0,35,500,35,fill = "blue2", width=2.0)
        for y in range(65, 300, 30):
            self.can.create_line(0,y,500,y,fill = "red2", width=2.0)
        #show text
        self.can.create_text(250,15, text=self.name.title(), font="arial 18")
        self.can.create_text(5,40, text="Ingredients:",
                             width=500, anchor = NW, font="arial 14")
        self.can.create_text(5,70, text=self.ingredients,
                             width=500, anchor = NW, font="arial 14")
        self.can.create_text(5,160, text="Comments:",
                             width=500, anchor = NW, font="arial 14")
        self.can.create_text(5,190, text=self.comments,
                             width=500, anchor = NW, font=("Comic Sans MS", 14))
        
##run application
root = Tk()
root.title("Bott Family Recipe Finder")
app = Application(root)
#create add window
add_recipe = AddWindow(app)
add_recipe.withdraw()
#create menu bar
menu_bar = Menu(root, tearoff=False)
menu_bar.add_command(label="Add Recipe", command = add_recipe.show)
root.config(menu=menu_bar)
#run
root.mainloop()
