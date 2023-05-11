from tkinter import *
import datacontainer
from tkinter import filedialog, simpledialog, messagebox
from tksimplestatusbar import StatusBar

from lbdialogs import tkLevelDialog, tkTextViewer, tkLevelPacksList
from common_dialogs import *
import tempfile

import icons

import os, sys


os.chdir(os.path.dirname(os.path.abspath(__file__)))

#
#
# MAIN LEVEL EDITOR SCREEN
#
#
class PykurinLevelEditorUI(Frame):

    #Button identifiers
    BASHER_BUTTON  = 0
    BOUNCER_BUTTON = 1
    LIVES_BUTTON   = 2
    PAN_BUTTON     = 3
    SELECT_BUTTON  = 4

    def __init__(self, master=None):
        Frame.__init__(self, master, relief=SUNKEN, bd=2)


        #Import the icons. (needs tk running, that is why it is done inside
        #the function and not on the top of the module
        self.ICONS = icons.icons_from_dir()

        self.__guibuild_menubar()
        self.__guibuild_toolbar()
        self.__guibuild_statusbar()
        self.__guibuild_canvas()

        #Force the search of a pykurin directory
        bdir = filedialog.askdirectory()
        if not bdir:
            sys.exit()
        if not datacontainer.isPykurinDirectory(bdir):
            error_message("ERROR", "%s is not a Pykurin game directory" % bdir)
            sys.exit()

        self.DC = datacontainer.LevelContainer(pykurindir=bdir)

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            self.master.tk.call(master, "config", "-menu", self.menubar)

        #PAN
        self.panx  = 0
        self.pany  = 0
        self.ppx   = None
        self.ppy   = None

        #Selected item
        self.sitem = None

        #ID dictionary between GUI and LevelContainer
        self.dataids = {}

        #Window title
        self.changeWindowTitle("TK pykurin Level builder")


    #
    # GUI BUILD FUNCTIONS
    #
    def __guibuild_menubar(self):

        #The Menu bar
        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="New Level",     command=self.f_new_level)
        menu.add_command(label="Open Level",    command=self.f_open_level)
        menu.add_command(label="Save Level",    command=self.f_save_level)
        menu.add_command(label="Save Level As", command=self.f_save_level_as)
        menu.add_command(label="Deploy",        command=self.f_deploy_to_pykurin)
        menu.add_command(label="Exit",          command=self.f_exit)

        menu = Menu(self.menubar, tearoff=0)
        showImage      = BooleanVar()
        showBackground = BooleanVar()
        showCollisions = BooleanVar()
        showItems      = BooleanVar()
        showMonsters   = BooleanVar()

        self.view_menu_items = [showImage, showBackground, showCollisions,
                showMonsters, showItems]

        self.menubar.add_cascade(label="View", menu=menu)
        menu.add_checkbutton(label="Game Image", variable=showImage,
                            onvalue=True, offvalue=False,
                            command=lambda: self.v_toggle(0, ["playBG"]))
        menu.add_checkbutton(label="Background", variable=showBackground,
                            onvalue=True, offvalue=False,
                            command=lambda: self.v_toggle(1, ["bgBG"]))
        menu.add_checkbutton(label="Collisions", variable=showCollisions,
                            onvalue=True, offvalue=False,
                            command=lambda: self.v_toggle(2, ["colBG"]))
        menu.add_checkbutton(label="Monsters",   variable=showMonsters,
                            onvalue=True, offvalue=False,
                            command=lambda: self.v_toggle(3, ["basher", "basher_end"]))
        menu.add_checkbutton(label="Items",      variable=showItems,
                            onvalue=True, offvalue=False,
                            command=lambda: self.v_toggle(4, ["bouncer", "lives"]))

        for var in self.view_menu_items:
            var.set(True)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Level", menu=menu)
        menu.add_command(label="Edit", command=self.e_edit_level_attributes)
        menu.add_command(label="LevelPacks", command=self.e_edit_level_packs)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Test", menu=menu)
        menu.add_command(label="Run Level", command=self.run_level)


    def __guibuild_toolbar(self):

        # The toolbar to create things
        toolbar = Frame(self.master)

        self.buttons = []

        b = Button(toolbar, image=self.ICONS["select24"], text="Select",
                   #compound=LEFT, #COmbine text and icon
                   padx=8, pady=8,
                   command=lambda: self.button(self.SELECT_BUTTON, 0))
        b.pack(side=LEFT, padx=2, pady=2)
        b.config(relief=SUNKEN)
        self.buttons.append(b)

        b = Button(toolbar, image=self.ICONS["move24"], text="Pan",
                   #compound=LEFT, #COmbine text and icon
                   padx=8, pady=8,
                   command=lambda: self.button(self.PAN_BUTTON, 1))
        b.pack(side=LEFT, padx=2, pady=2)
        self.buttons.append(b)

        b = Button(toolbar, text="Bouncer", image=self.ICONS["bouncer_icon_24"],
                   #compound=LEFT, #COmbine text and icon
                   padx=8, pady=8,
                   command=lambda: self.button(self.BOUNCER_BUTTON, 2))
        b.pack(side=LEFT, padx=2, pady=2)
        self.buttons.append(b)

        b = Button(toolbar, text="lifeup", image=self.ICONS["live_icon_24"],
                   #compound=LEFT, #COmbine text and icon
                   padx=8, pady=8,
                   command=lambda: self.button(self.LIVES_BUTTON, 3))
        b.pack(side=LEFT, padx=2, pady=2)
        self.buttons.append(b)

        b = Button(toolbar, image=self.ICONS["basher_icon_24"], text="basher",
                   #compound=LEFT, #COmbine text and icon
                   padx=8, pady=8,
                   command=lambda: self.button(self.BASHER_BUTTON, 4))
        b.pack(side=LEFT, padx=2, pady=2)
        self.buttons.append(b)

        #Contains the currently pressed button. Not the index but the type of the item to create
        #DC.BASHER (for example)
        self.buttonpressed = None
        toolbar.pack(side=TOP, fill=X)


    def __guibuild_statusbar(self):
        # Status bar with the x y information
        self.statusbar = StatusBar(self.master)
        self.statusbar.pack(side=BOTTOM, fill=X)

    def __guibuild_canvas(self):
        self.canvas = Canvas(self, bg="gray", width=800, height=600,
                     bd=0, highlightthickness=0)
        self.canvas.pack()

        #Bind Mouseover on Canvas
        self.canvas.bind("<Motion>", self.mouse_motion)

        #Bind Center click to pan
        self.canvas.bind("<B2-Motion>", self.pan_motion)
        self.canvas.bind("<Button-2>", self.pan_start)

        #Bind clicking to select
        self.canvas.bind("<Button-1>", self.canvas_left_click)
        self.canvas.bind("<B1-Motion>", self.canvas_left_click_motion)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_left_click_release)

        #Bind clicking to select
        self.canvas.bind("<Delete>", self.delete_item)


    #
    # Canvas draw toggle
    #
    def v_toggle(self, buttonid, taglist):
        for tag in taglist:
            for item in self.canvas.find_withtag(tag):
                if self.view_menu_items[buttonid].get():
                    self.canvas.itemconfig(item, state=NORMAL)
                else:
                    self.canvas.itemconfig(item, state=HIDDEN)

    #
    # Some getters
    #
    def get_item_type(self, itemid):
        return self.dataids[itemid][0]

    def isBasher(self, itemid):
        return self.get_item_type(itemid) == self.DC.BASHER

    def isBasherEnd(self, itemid):
        return self.get_item_type(itemid) == self.DC.BASHER_END

    def changeWindowTitle(self, title):
        self.master.wm_title(title)

    #
    # Toolbar selection handling
    #
    def unsunken_all(self):
        for b in self.buttons:
            b.config(relief=RAISED)

    def isButtonPressed(self):
        return self.buttonpressed != None

    def button(self, code, buttonid):
        self.unsunken_all()
        if self.buttonpressed == code:
            self.buttons[buttonid].config(relief=RAISED)
            self.buttonpressed = None
        else:
            self.buttons[buttonid].config(relief=SUNKEN)
            self.buttonpressed = code

        #Let the select button always be pressed
        if not self.isButtonPressed():
            self.buttons[0].config(relief=SUNKEN)

        if code != self.SELECT_BUTTON:
            self.unselect_everything()


    def unselect_everything(self):
        """Removes all selections"""
        #Delete all selections
        self.canvas.delete("selection")
        self.sitem = None

    #
    # Running a level
    #
    def run_level(self):
        """Run the current level by the specified pykurin base dir"""
        bdir = self.DC.get_pykurindir()
        pykurinexe = os.path.join(bdir,"pykurin.py")

        #Check for errors on save Before trying Anything
        if self._save_level_errcheck(): return

        #Check if all data is in pykurin directory, if not copy, if not end
        if not self.manage_data_dialogs():
            return


        #Create a temporary file, save the level, run and delete
        tmpfile = tempfile.NamedTemporaryFile()


        self.__f_save(tmpfile.name)

        os.system("/usr/bin/python %s %s" % (pykurinexe, tmpfile.name))

        #os.unlink(tmpfile.name)

    #
    # Panning
    #
    def mouse_motion(self, event):
        self.statusbar.set("%s : %s" % (event.x - self.panx, event.y - self.pany))

    def pan_start(self, event):
        self.ppx = event.x
        self.ppy = event.y

    def pan_motion(self, event):
        canvas = self.canvas
        px = self.ppx - event.x
        py = self.ppy - event.y

        self.panx -= px
        self.pany -= py

        #Pan the objects tagged as PAN.
        for item in canvas.find_withtag("pan"):
            canvas.move(item, -px, -py)

        self.pan_start(event)

    #
    # Item selection and creating
    #
    def canvas_left_click(self, event):
        """ May select/unselect an Item.
            If any creation tool is active may create one of the selected items

        """
        if (self.buttonpressed == self.SELECT_BUTTON
            or not self.isButtonPressed()):
            self.selecting_items(event)
        else:
            self.adding_item_to_canvas(event)

    def selecting_items(self, event):
        #Once clicked, give keyboard focus to canvas (in case it wasn't set)
        self.canvas.focus_set()

        x = event.x
        y = event.y

        #Delete all selections
        self.unselect_everything()

        #Create a new selection
        self.select_item(x,y)

    def adding_item_to_canvas(self, event):
        if self.buttonpressed == self.BASHER_BUTTON:
            self._create_basher(event.x, event.y, new=True)
        elif self.buttonpressed == self.BOUNCER_BUTTON:
            self._create_bouncer(event.x, event.y, new=True)
        elif self.buttonpressed == self.LIVES_BUTTON:
            self._create_lives(event.x, event.y, new=True)
        elif self.buttonpressed == self.PAN_BUTTON:
            self.pan_start(event)

    def select_item(self, x, y):
        """Selects an item, setting the sitem attribute"""
        c = self.canvas
        items = self.canvas.find_overlapping(x-2,y-2,x+2,y+2)

        #Just interested in the selectable items
        pitems = []

        for i in items:
            if "select" in c.gettags(i):
                pitems.append(i)

        self.sitem = None
        if pitems:
            self.sitem = pitems[0]

        if self.sitem:
            c.create_rectangle(c.bbox(self.sitem), tags=("pan","selection"),
                                                   outline="red", width=2)

    #
    # Item moving
    #
    def canvas_left_click_motion(self, event):
        """This motion is responsible mainly for the movement of the items"""

        #If the pan button is pressed, PAN as it would be done with middle
        #button
        if self.buttonpressed == self.PAN_BUTTON:
            self.pan_motion(event)
            return

        if not self.sitem:
            return

        #If item selected Move that item
        bbox  = self.canvas.bbox(self.sitem)
        w     = abs(bbox[0] - bbox[2])
        h     = abs(bbox[1] - bbox[3])
        self.canvas.coords(self.sitem, (event.x -w/2, event.y -h/2))

        #Move the selection
        for item in self.canvas.find_withtag("selection"):
            self.canvas.coords(item, self.canvas.bbox(self.sitem))

        #Basher needs a little bit more of work
        if self.isBasher(self.sitem) :
            self.update_basher_arrow(self.sitem)
        if self.isBasherEnd(self.sitem):
            basher_id = self.dataids[self.sitem][2]
            self.update_basher_arrow(basher_id)

    def unpan_bbox(self, bbox):
        """Return a bbox without the panning movements"""
        return (bbox[0] - self.panx, bbox[1] - self.pany, bbox[2] - self.panx, bbox[3] - self.pany)

    def canvas_left_click_release(self, event):
        if not self.sitem:
            return

        itype = self.dataids[self.sitem][0]
        iid   = self.dataids[self.sitem][1]
        bbox  = self.unpan_bbox(self.canvas.bbox(self.sitem))

        self.DC.move_item(itype, iid, bbox[0], bbox[1])

    def update_basher_arrow(self, basherid):
        """Update the arrow representing the path of the BASHER.
            This needs updating everytime the basher or basher end changes
            position
        """
        basher_line   = self.dataids[basherid][3]
        basher_end    = self.dataids[basherid][2]
        basher_coords = self.canvas.bbox(basherid)
        end_coords    = self.canvas.bbox(basher_end)

        bwidth        = abs(basher_coords[0] - basher_coords[2])
        bheight       = abs(basher_coords[1] - basher_coords[3])

        ewidth        = abs(end_coords[0] - end_coords[2])
        eheight       = abs(end_coords[1] - end_coords[3])

        lbbox         = ( basher_coords[0] + bwidth  / 2,
                          basher_coords[1] + bheight / 2,
                          end_coords[0]    + ewidth  / 2,
                          end_coords[1]    + eheight / 2
                        )

        self.canvas.coords(basher_line, lbbox)

    #
    # Remove items
    #
    def delete_item(self, event):
        """Deletes the current selected item"""
        if not self.sitem:
            print("No item selected")
            return

        itype = self.dataids[self.sitem][0]
        if itype == self.DC.BASHER:
            dcid = self.dataids[self.sitem][1]

            # Canvas ids of the other basher parts
            rectid = self.dataids[self.sitem][2]
            lineid = self.dataids[self.sitem][3]

            #delete from canvas
            self.canvas.delete(self.sitem)
            self.canvas.delete(rectid)
            self.canvas.delete(lineid)

            self.DC.remove_item(itype, dcid)

        else:
            dcid = self.dataids[self.sitem][1]
            #Delete from the container
            self.DC.remove_item(itype, dcid)

            self.canvas.delete(self.sitem)

        self.__update_dataids_after_remove(itype, dcid)
        self.unselect_everything()


    #
    # Handling references to data ids
    #
    def __update_dataids_after_remove(self, itype, dcid):
        """Update all the indexes after the removal of one
        of the objects.
            This is kind of ugly because the ids of LevelContainer
            are just the indexes. So removing one object from there
            implies invalidating most of the indexes here.
        """
        for tkid,dcdata in self.dataids.items():
            dtype = dcdata[0]
            if dtype == itype:
                if dcdata[1] > dcid:
                    if itype == self.DC.BASHER:
                        self.dataids[tkid] = (itype, dcdata[1] - 1,
                                              dcdata[2], dcdata[3])
                    else:
                        self.dataids[tkid] = (itype, dcdata[1] - 1)

    #
    # MENU HANDLING. SAVE; LOAD; NEW; EXIT
    #

    def manage_level_data(self):
        log = []
        isalldata, outsidedata = self.DC.isAllDataInPykurinDirectory()

        if isalldata:
            log.append("All data is in pykurin environment")
            return log

        cplist = self.DC.copyOutsidersToPykurinDirectory()
        log.append("Copying data to deploy")
        for c in cplist:
            log.append(c)

        return log

    def manage_data_dialogs(self):
        """ This flow of dialogs does the following:
         - Checks if LevelContainer has all the files pointed to the pykurin directory
         - If not, asks for a possible copy of data (if the user wants it)
         - Tries to copy all the data and presents the user with the copy
            information

            Success returns True (the level is on a pykurin directory)
            False -> The level can't be run, as it is not a pykurin directory

        """
        isalldata, outsidedata = self.DC.isAllDataInPykurinDirectory()
        if not isalldata:
            if self.copy_data_dialog(outsidedata):
                #Get ready to copy files
                try:
                    cplist = self.DC.copyOutsidersToPykurinDirectory()
                except Exception as e:
                    error_message("ERROR",e)
                    return False

                tkTextViewer(self.master, title="COPY LOG",
                        textdata="COPIED\n%s"%"\n".join(cplist), islog=True)
                return True
            else:
                return False
        else:
            return True


    def copy_data_dialog(self, files):
        files_str = "\n".join(files)
        return ask_dialog("COPY NEEDED",
        """The following files are not in the correct path:

%s.

Do you want to copy the files to the game levelpack tree?
        """% (files_str)
        )

    def f_new_level(self):
        """ Creates a new level with no file associated to it """
        print("NEW LEVEL")

        # Force a new LevelContainer
        basep   = self.DC.get_basepath()
        self.DC = datacontainer.LevelContainer()
        self.DC.set_pykurindir(basep) #Keep the pykurin directory

        #Start and end are created automatically
        self.DC.add_item(self.DC.STICKS, 0, 0)
        self.DC.add_item(self.DC.GOALS,  100, 100)

        self._create_canvas_with_DC()

    def f_open_level(self):
        """
            Opens a file chooser to load a properties image
        """
        filepath = open_file_chooser("Properties",
                                    ".prop",
                                    self.DC.get_basepath());
        if os.path.isfile(filepath):
            #clear_paddings()
            self.DC.load_from_file(filepath)

        self._create_canvas_with_DC()

    def _save_level_errcheck(self):
        """Checks for errors, Returns true if an error is found"""
        save , why = self.DC.isSaveable()
        if not save:
            error_message("Can't Save", why)
            return True
        return False

    def __f_save(self, fname):
        """Try to save the level to the specified filename"""

        if fname:
            ret, msg = self.DC.save_to_file(fname)
            if ret:
                popup_message("SUCCESS","%s saved" % fname)
            else:
                error_message("ERROR","File %s NOT saved\n %s" % (fname, msg))
        else:
            error_message("Invalid Filename %s" % fname)

    def f_save_level(self):
        if self._save_level_errcheck():
            return

        fname = self.DC.get_current_level_filename()
        if not fname:
            self.f_save_level_as()
        else:
            self.__f_save(fname)

    def f_save_level_as(self):
        if self._save_level_errcheck():
            return

        fname = save_file_chooser("Save As")
        self.__f_save(fname)

    def f_exit(self):
        self.master.destroy()

    def f_deploy_to_pykurin(self):
        #Check for errors before attempting a save
        if self._save_level_errcheck(): return

        if not ask_dialog("DEPLOY", "Save the level an all its files to pykurin directory"):
            return

        #if not self.manage_data_dialogs():
        #    return

        fname    = self.DC.get_deploy_filename()
        log      = self.manage_level_data()
        ret, msg = self.DC.save_to_file(fname)

        data     =   log

        if ret:
            data += ["DEPLOYED TO %s"%fname]
        else:
            data += ["ERROR SAVING %s: %s"%(fname, msg)]

        tkTextViewer(self.master, title="DEPLOY LOG",
                textdata="\n".join(data), islog=True)



    def e_edit_level_attributes(self):
        tkLevelDialog(self.master, levelcontainer=self.DC)
        self._create_backgrounds()

    def e_edit_level_packs(self):
        tkLevelPacksList(self.master, pykurindir=self.DC.get_pykurindir())


    #
    # Item Creation
    #
    def _create_bouncer(self, x, y, dcid=None, new=False):
        canvas = self.canvas
        dc     = self.DC

        id = canvas.create_image((x, y),
                            image=self.ICONS["bouncer"], anchor=NW,
                            tags=("select", "move", "bouncer", "delete", "pan"))

        if new:
            bbox = self.unpan_bbox(canvas.bbox(id))
            dcid = dc.add_item(self.DC.BOUNCER, bbox[0], bbox[1])

        self.dataids[id] = (dc.BOUNCER, dcid)

    def _create_lives(self, x, y, dcid=None, new=False):
        canvas = self.canvas
        dc     = self.DC

        id = canvas.create_image((x, y),
                            image=self.ICONS["live"], anchor=NW,
                            tags=("select", "move", "delete", "lives", "pan"))

        if new:
            bbox = self.unpan_bbox(canvas.bbox(id))
            dcid = dc.add_item(self.DC.LIVES, bbox[0], bbox[1])

        self.dataids[id] = (dc.LIVES, dcid)


    def _create_basher(self, x, y, rx=None, ry=None, dcid=None, new=False):
        """
            Create a basher to add to the canvas and LevelContainer.
            By default the basher is only created in the canvas, to be
            saved in the LevelContainer the new flag has to be set to true
        """
        canvas = self.canvas
        dc     = self.DC

        if not rx:
            rx = x + 100
        if not ry:
            ry = y


        idl = canvas.create_line(0,0,0,0,tags = ("pan", "basher"))

        ids = canvas.create_image((rx, ry),
                            image=self.ICONS["basher_goto"], anchor=NW,
                            tags=("select", "move", "pan", "basher"))

        idb = canvas.create_image((x, y),
                            image=self.ICONS["basher"], anchor=NW,
                            tags=("select", "move", "pan", "basher"))

        #If its new, it can't have an dcid. Create and get the dcid first
        if new:
            bboxb = self.unpan_bbox(canvas.bbox(idb))
            bboxe = self.unpan_bbox(canvas.bbox(ids))
            dcid = dc.add_item(self.DC.BASHER, bboxb[0], bboxb[1])
            dc.add_item(self.DC.BASHER_END, bboxe[0], bboxe[1])


        self.dataids[idb] = (dc.BASHER, dcid, ids, idl)
        self.dataids[ids] = (dc.BASHER_END, dcid, idb, idl)
        self.dataids[idl] = (-1, dcid)

        self.update_basher_arrow(idb)

    def _create_backgrounds(self):
        canvas = self.canvas
        dc     = self.DC

        canvas.delete("backgrounds")

        imgpath = dc.get_background_fname()
        if imgpath:
            self.bgimage  = icons.load_tkimage(imgpath)
            canvas.create_image((0,0),
                                image=self.bgimage, anchor=NW,
                                tags = ("backgrounds", "bgBG")
                                )

        imgpath = dc.get_colision_fname()
        if imgpath:
            self.colimg   = icons.load_tkimage(imgpath)
            canvas.create_image((0 + self.panx,0 + self.pany),
                                image=self.colimg, anchor=NW,
                                tags = ("pan", "backgrounds", "colBG")
                                )


        imgpath = dc.get_image_fname()
        if imgpath:
            self.frontimg = icons.load_tkimage(imgpath)
            canvas.create_image((0 + self.panx ,0 + self.pany),
                            image=self.frontimg, anchor=NW,
                            tags = ("pan", "backgrounds", "playBG"))

        canvas.tag_lower("backgrounds")


    def _create_canvas_with_DC(self):
        """
            Create a canvas from the DC.
        """
        canvas = self.canvas
        dc     = self.DC
        canvas.delete(ALL)
        self.panx = self.pany = 0

        self._create_backgrounds()


        #Filled with pygame RECTS
        for idx,r in enumerate(dc.bouncers):
            self._create_bouncer(r.x, r.y, dcid=idx)

        for idx,r in enumerate(dc.lives):
            self._create_lives(r.x, r.y, dcid=idx)

        for idx,r in enumerate(dc.goals):
            id = canvas.create_image((r.x, r.y),
                                image=self.ICONS["goal"], anchor=NW,
                                tags=("select", "move", "goal", "pan"))

            self.dataids[id] = (dc.GOALS, idx)

        for idx,r in enumerate(dc.sticks):
            id = canvas.create_image((r.x, r.y),
                                image=self.ICONS["stick"], anchor=NW,
                                tags=("select", "move", "stick", "pan")
                                )

            self.dataids[id] = (dc.STICKS, idx)

        for idx,r in enumerate(dc.bashers):
            r1 = r
            r2 = dc.bashers_end[idx]
            self._create_basher(r1.x, r1.y, rx=r2.x, ry=r2.y, dcid=idx)

        # Draw the 0,0 cross
        canvas.create_line(10, 0, -10, 0, fill="red", tags=("pan"))
        canvas.create_line(0, 10, 0, -10, fill="red", tags=("pan"))


root = Tk()

app = PykurinLevelEditorUI(root)
app.pack()

#show_disclaimer()
root.mainloop()
