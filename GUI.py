from tkinter import *
from PIL import Image, ImageTk
import os

# Basic window
root = Tk()
root.title("Game name")
root.geometry("1200x800") # change the size of screen
root.configure(bg="#f4f4f4") # change background color

# Every plot

pages = {
    "START": {
        "type": "start",
        "title": "Game name",
        "text": "Text()\n\nClick Start to begin.",
        "bg": "images/Start.png"
    },

    "N1": {
        "type": "next",
        "title": "Background",
        "text": (
            "Text"
        ),
        "next": "N2",
        "bg":"images/Background.png"
    },

    "N2": {
        "type": "next",
        "title": "Call",
        "text": (
            "Text"
        ),
        "next": "N3",
        "bg":"images/Call.png"
    },

    "N3": {
        "type": "next",
        "title": "Mansion",
        "text": (
            "Text"
        ),
        "next": "N4",
        "bg":"images/Mansion.png"
    },

    "N4": {
        "type": "next",
        "title": "Library",
        "text": (
            "Text"
        ),
        "next": "N5",
        "bg":"images/Library.png"
    },

    "N5": {
        "type": "choice",
        "title": "Q1: Choose One Person",
        "text": (
            "Question1"
        ),
        "choice1_text": "Q1A - Security Guard",
        "choice1_next": "N6",
        "choice2_text": "Q1B - Sophia",
        "choice2_next": "N13",
        "bg":"images/Q1.png"
    },

    "N6": {
        "type": "next",
        "title": "Security Guard",
        "text": (
            "Text"
        ),
        "next": "N7",
        "bg":"images/Security Guard.png"
    },

    "N7": {
        "type": "choice",
        "title": "Q2: Believe or Not",
        "text": (
            "Q2"
        ),
        "choice1_text": "Q2A - Believe",
        "choice1_next": "N8",
        "choice2_text": "Q2B - Not Believe",
        "choice2_next": "N11"
    },

    "N8": {
        "type": "next",
        "title": "Garden Trail",
        "text": (
            "Text"
        ),
        "next": "N9",
        "bg":"images/Garden trail.png"
    },

    "N9": {
        "type": "next",
        "title": "Basement",
        "text": (
            "Text"
        ),
        "next": "END_1",
        "bg":"images/Basement.png"
    },

    "END_1": {
        "type": "ending",
        "title": "Ending",
        "text": (
            "Text1"
        ),
        "analyze_next": "ANALYZE_1"
    },

    "ANALYZE_1": {
        "type": "analyze",
        "title": "Analyze",
        "text": (
            "Analysis:\n\n"
            "Text"
        )
    },

    "N11": {
        "type": "next",
        "title": "CCTV Room",
        "text": (
            "Text"
        ),
        "next": "END_2",
        "bg": "images/CCTV.png"
    },

    "END_2": {
        "type": "ending",
        "title": "Ending",
        "text": (
            "Text"
        ),
        "analyze_next": "ANALYZE_2"
    },

    "ANALYZE_2": {
        "type": "analyze",
        "title": "Analyze",
        "text": (
            "Analysis:\n\n"
            "Text"
        )
    },

    "N13": {
        "type": "next",
        "title": "Sophia",
        "text": (
            "Text"
        ),
        "next": "N14",
        "bg": "images/Sophia.png"
    },

    "N14": {
        "type": "choice",
        "title": "Q2: Choose One Route",
        "text": (
            "Q2"
        ),
        "choice1_text": "Q2A - Adrian",
        "choice1_next": "N15",
        "choice2_text": "Q2B - Finances",
        "choice2_next": "N19"
    },

    "N15": {
        "type": "next",
        "title": "Parking Lot",
        "text": (
            "Text"
        ),
        "next": "N16",
        "bg": "images/Parking lot.png"
    },

    "N16": {
        "type": "next",
        "title": "Kitchen",
        "text": (
            "Text"
        ),
        "next": "N17",
        "bg": "images/Kitchen.png"
    },

    "N17": {
        "type": "next",
        "title": "Victor's Private Office",
        "text": (
            "Text"
        ),
        "next": "END_3",
        "bg": "images/Victor's private office.png"
    },

    "END_3": {
        "type": "ending",
        "title": "Ending",
        "text": (
            "Text"
        ),
        "analyze_next": "ANALYZE_3"
    },

    "ANALYZE_3": {
        "type": "analyze",
        "title": "Analyze",
        "text": (
            "Analysis:\n\n"
            "Text"
        )
    },

    "N19": {
        "type": "next",
        "title": "Finance Office",
        "text": (
            "Text"
        ),
        "next": "N20",
        "bg": "images/Finance office.png"
    },

    "N20": {
        "type": "next",
        "title": "Archive Room",
        "text": (
            "Text"
        ),
        "next": "END_4",
        "bg": "images/Archive room.png"
    },

    "END_4": {
        "type": "ending",
        "title": "Ending",
        "text": (
            "Text"
        ),
        "analyze_next": "ANALYZE_4"
    },

    "ANALYZE_4": {
        "type": "analyze",
        "title": "Analyze",
        "text": (
            "Analysis:\n\n"
            "Text"
        )
    }
}


# Confirm the first page
current_page = "START"

#Background label
background_label = Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# All widgets
title_label = Label(
    root,
    text="",
    font=("Arial", 28, "bold"),
    bg="#111111",
    fg="white",
)

story_text = Text(
    root,
    width=90,
    height=7,
    font=("Arial", 15),
    wrap=WORD,
    bg="#111111", #Black text box
    fg="white", #White letters
    insertbackground="white",
    relief="flat",
    padx=10,
    pady=15
)

main_button = Button(
    root,
    text="",
    font=("Arial", 15),
    width=14,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)

choice_frame = Frame(root, bg="#111111")
choice_button1 = Button(
    choice_frame,
    text="",
    font=("Arial", 14),
    width=18,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)
choice_button2 = Button(
    choice_frame,
    text="",
    font=("Arial", 14),
    width=18,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)

ending_frame = Frame(root, bg="#111111")
analyze_button = Button(
    ending_frame,
    text="Analyze",
    font=("Arial", 14),
    width=12,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)
restart_button = Button(
    ending_frame,
    text="Restart",
    font=("Arial", 14),
    width=12,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)
exit_button = Button(
    ending_frame,
    text="Exit",
    font=("Arial", 14),
    width=12,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)

analyze_page_frame = Frame(root, bg="#111111")
restart_button2 = Button(
    analyze_page_frame,
    text="Restart",
    font=("Arial", 14),
    width=12,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)
exit_button2 = Button(
    analyze_page_frame,
    text="Exit",
    font=("Arial", 14),
    width=12,
    height=2,
    bg="#111111",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    highlightbackground="white",
    highlightcolor="white",
    highlightthickness=2
)


# Functions
# change background image
def set_background(image_path):
    global bg_photo

    base_path = os.path.dirname(os.path.abspath(__file__))  # Current directory file
    full_path = os.path.join(base_path, image_path)

    print("BASE PATH:", base_path)
    print("IMAGE PATH:", image_path)
    print("FULL PATH:", full_path)
    print("EXISTS:", os.path.exists(full_path))
    print("FILES IN IMAGES:", os.listdir(os.path.join(base_path, "images")))

    image = Image.open(full_path)
    image = image.resize((1200, 800))
    bg_photo = ImageTk.PhotoImage(image)

    background_label.config(image=bg_photo)
    background_label.lower()

def go_to_page(page_id):
    global current_page
    current_page = page_id
    show_page()


def start_game():
    go_to_page("N1")


def next_page():
    next_id = pages[current_page]["next"]
    go_to_page(next_id)


def restart_game():
    go_to_page("START")


def exit_game():
    root.destroy()


def open_analyze():
    analyze_id = pages[current_page]["analyze_next"]
    go_to_page(analyze_id)


def clear_screen():
    title_label.pack_forget()

    story_text.pack_forget()
    story_text.place_forget()

    main_button.pack_forget()
    main_button.place_forget()

    choice_frame.pack_forget()
    choice_frame.place_forget()

    choice_button1.pack_forget()
    choice_button1.place_forget()
    choice_button2.pack_forget()
    choice_button2.place_forget()

    ending_frame.pack_forget()
    ending_frame.place_forget()
    analyze_button.pack_forget()
    restart_button.pack_forget()
    exit_button.pack_forget()

    analyze_page_frame.pack_forget()
    analyze_page_frame.place_forget()
    restart_button2.pack_forget()
    exit_button2.pack_forget()


def show_page():
    clear_screen()

    page = pages[current_page]

    if "bg" in page:
        set_background(page["bg"])

    #else:  #Set the default background for pages without images
        #background_label.config(image="")
        #root.configure(bg="#f4f4f4")

    title_label.config(text=page["title"])
    title_label.pack(pady=30)

    story_text.config(state=NORMAL)
    story_text.delete("1.0", END)
    story_text.insert(END, page["text"])
    story_text.place(relx=0.5, rely=0.78, anchor=CENTER)
    story_text.config(state=DISABLED) # Users can't edit

    if page["type"] == "start":
        main_button.config(text="Start", command=start_game)
        main_button.place(relx=0.5, rely=0.55, anchor=CENTER)

    elif page["type"] == "next":
        main_button.config(text="Next", command=next_page)
        main_button.place(relx=0.5, rely=0.55, anchor=CENTER)

    elif page["type"] == "choice":
        choice_frame.place(relx=0.5, rely=0.55, anchor=CENTER)

        choice_button1.config(
            text=page["choice1_text"],
            command=lambda: go_to_page(page["choice1_next"])
        )
        choice_button1.pack(side=LEFT, padx=15)

        choice_button2.config(
            text=page["choice2_text"],
            command=lambda: go_to_page(page["choice2_next"])
        )
        choice_button2.pack(side=LEFT, padx=15)

    elif page["type"] == "ending":
        ending_frame.place(relx=0.5, rely=0.55, anchor=CENTER)

        analyze_button.config(command=open_analyze)
        analyze_button.pack(side=LEFT, padx=15)

        restart_button.config(command=restart_game)
        restart_button.pack(side=LEFT, padx=15)

        exit_button.config(command=exit_game)
        exit_button.pack(side=LEFT, padx=15)

    elif page["type"] == "analyze":
        analyze_page_frame.place(relx=0.5, rely=0.55, anchor=CENTER)

        restart_button2.config(command=restart_game)
        restart_button2.pack(side=LEFT, padx=15)

        exit_button2.config(command=exit_game)
        exit_button2.pack(side=LEFT, padx=15)


show_page()
root.mainloop()