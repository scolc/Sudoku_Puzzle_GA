import random
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText

import grid_solver as gsol
import sudoku_grid as sg


class GUI():
    """
    A class to handle the GUI for accepting user input,
    call the genetic algorithm and display output for the user.
    """

    def __init__(self):
        self.ui = Tk()
        
        # Window proportions
        self.tile_size = 40 # Tile pixel size to base gui proportions on
        self.x_pad = int(self.tile_size / 2)
        self.y_pad = int(self.tile_size / 2)
        
        self.max_window_columns = 14 # Space for 9 grid columns, a button and padding in between
        self.max_window_rows = 18 # Space for 9 grid rows, other elements and padding
        
        self.window_width = self.max_window_columns * self.tile_size
        self.window_height = self.max_window_rows * self.tile_size
        
        # Set the window properties
        self.ui.title("Sudoku Puzzle Solver")
        self.ui.resizable(width = False, height = False)
        self.ui.geometry(str(self.window_width) + "x" + str(self.window_height))
        self.ui["bg"] = "#F8FEB5"

        # Colours for cells and other elements
        # Normal
        self.col_fg_en_norm = "#000000" 
        self.col_fg_dis_norm = "#525252"
        self.col_bg_en_norm = "#fafafa"
        self.col_bg_dis_norm = "#c8c8c8"

        # Puzzle clues for solution
        self.col_fg_dis_clue = "#2e00ff"

        # Hints
        self.col_hint = "#ffec00"
        
        # Validate
        self.col_valid = "#00ff19"
        self.col_invalid = "#ff0000"

        # Output box
        self.col_out_fg = "#ffffff"
        self.col_out_bg = "#000000"

        # Initialise the ui elements
        # Title Box
        self.title_box_width = self.window_width - 2 * self.x_pad
        self.title_box_height = self.tile_size * 1.5
        self.title_font = "Calibri " + str(int(self.tile_size / 1.25))
        
        self.title_box = Label(self.ui, text = "Sudoku Puzzle Solver")
        self.title_box["font"] = self.title_font

        # Grid
        self.grid_ui = self.init_grid_ui()
        self.grid_size = 9 * self.tile_size

        # Buttons
        self.btn_height = self.tile_size
        # Dynamic width between grid and window side border
        self.btn_width = self.window_width - (self.grid_size + 3 * self.x_pad)
        
        self.btn_font = "Calibri " + str(int(self.tile_size / 2.5))
        #self.btn_pad = 1

        self.solve_btn = Button(self.ui, text = "START",
                                font = self.btn_font,
                                command = self.solve_btn)
        self.show_sol_btn = Button(self.ui, text = "Show Solution",
                                font = self.btn_font,
                                command = self.show_solution,
                                state = "disabled")
        self.show_hint_btn = Button(self.ui, text = "Show Hint",
                                font = self.btn_font,
                                command = self.show_hint,
                                state = "disabled")
        self.valid_entry_btn = Button(self.ui, text = "Validate",
                                font = self.btn_font,
                                command = self.validate_user_entry,
                                state = "disabled")
        self.clear_entry_btn = Button(self.ui, text = "Clear Entries",
                                font = self.btn_font,
                                command = self.clear_entries,
                                state = "disabled")
        self.reset_btn = Button(self.ui, text = "RESET GRID",
                                font = self.btn_font,
                                command = self.reset_grid)

        # Output Box
        self.output_width = self.window_width - 2 * self.x_pad
        # Dynamic height between element above and window bottom border
        self.output_height = self.window_height - (self.title_box_height +
                                                    self.grid_size +
                                                    4 * self.y_pad)
        self.output_font = "Calibri " + str(int(self.tile_size / 3))
        self.output_box = ScrolledText(self.ui,
                                        fg = self.col_out_fg,
                                        bg = self.col_out_bg,
                                        font = self.output_font,
                                        wrap = WORD,
                                        state = "disabled",
                                        padx = 5,
                                        pady = 5)
        self.output_box.tag_config("hint", foreground = self.col_hint)
        self.output_box.tag_config("valid", foreground = self.col_valid)
        self.output_box.tag_config("invalid", foreground = self.col_invalid)
        self.output_box.tag_config("normal", foreground = self.col_out_fg)
        
        

        # Other Variables
        self.running_ga = False
        self.ga_thread = threading.Thread()
        self.grid = sg.SudokuGrid()


    # Initialisation Functions

    def init_grid_ui(self):
        """
        A function to create the grid ui element.
        """
        new_grid = []
        for entry in range(9):
            new_grid.append(self.init_row_ui())
        
        return new_grid

    def init_row_ui(self):
        """
        A function to create a new row of entry boxes for the grid ui.
        """
        new_row = []
        for entry in range(9):
            valid_entry = (self.ui.register(self.validate_entry), '%P')
            cell = Entry(self.ui, borderwidth = 2, justify="center", validate = "key", validatecommand = valid_entry)
            cell["font"] = "Calibri " + str(int(self.tile_size / 2))
            cell["fg"] = self.col_fg_en_norm
            cell["disabledforeground"] = self.col_fg_dis_norm
            cell["bg"] = self.col_bg_en_norm
            cell["disabledbackground"] = self.col_bg_dis_norm
            new_row.append(cell)
        
        return new_row

    def validate_entry(self, entry):
        """
        A function to validate the value entered into any cell
        should always be a digit between 1 and 9 and refuses
        any other entry.
        """
        if len(entry) == 0:
            return True
        elif len(entry) == 1 and entry.isdigit():
            if entry not in "0":
                return True
            else:
                return False
        else:
            return False

    def init_output_box(self):
        """
        A function to set the output box initial state.
        """
        self.output_box["state"] = "normal"
        self.output_box.delete(1.0, END)
        message = "Please enter the initial clues (digits 1-9) for the puzzle into the grid above.\n"
        message += "Click 'START' to find the solution.\n"
        message += "Click 'RESET GRID' to clear the grid.\n\n"
        self.output(message)

    # Display Functions

    def display_title_box(self):
        """
        A function to display the title box.
        """
        self.title_box.place(x = self.x_pad,
                            y = self.y_pad,
                            width = self.title_box_width,
                            height = self.title_box_height)

    def display_grid_ui(self):
        """
        A function to display the grid ui.
        """
        for entry in range(len(self.grid_ui)):
            self.display_row_ui(self.grid_ui[entry], entry)

    def display_row_ui(self, this_row, row_num):
        """
        A function to display each row of the grid.
        """
        cell_pad = 1
        x_pos = self.x_pad + cell_pad
        y_pos = self.y_pad * 2 + self.title_box_height + cell_pad
        for entry in range(len(this_row)):
            this_row[entry].place(x = (entry * self.tile_size) + x_pos, 
                                y = (row_num * self.tile_size) + y_pos,
                                width = self.tile_size - 2 * cell_pad,
                                height = self.tile_size - 2 * cell_pad)
    
    def display_buttons(self):
        """
        A function to display the buttons for the user interaction.
        """
        # Create a button list to iterate over
        btn_list = []
        btn_list.append(self.solve_btn)
        btn_list.append(self.show_sol_btn)
        btn_list.append(self.show_hint_btn)
        btn_list.append(self.valid_entry_btn)
        btn_list.append(self.clear_entry_btn)
        btn_list.append(self.reset_btn)

        # Button positioning variables
        x_pos = self.grid_size + 2 * self.x_pad
        y_pos = self.title_box_height + 2 * self.y_pad
        
        if len(btn_list) > 1:
            empty_y_space = self.grid_size - len(btn_list) * self.btn_height
            y_space = empty_y_space / (len(btn_list) - 1) + self.btn_height
        else: # In case there is only 1 button created in error
            y_space = 0
        
        # Place buttons
        for button in btn_list:
            button.place(x = x_pos,
                        y = y_pos,
                        width = self.btn_width,
                        height = self.btn_height)
            y_pos += y_space

    def display_output_box(self):
        """
        A function to display the output box.
        """
        y_pos = self.title_box_height + self.grid_size + 3 * self.y_pad

        self.output_box.place(x = self.x_pad,
                        y = y_pos,
                        width = self.output_width,
                        height = self.output_height)

    def display_window(self):
        """
        A function to display the various elements of the window to
        allow the user interaction and run the various program functions
        """
        # Add title box
        self.display_title_box()

        # Add the grid
        self.display_grid_ui()

        # Add buttons
        self.display_buttons()

        # Add output box
        self.display_output_box()
        self.init_output_box()
        
        # Display the window
        self.ui.mainloop()
        

    def output(self, text : str, tag = "normal"):
        """
        A function to add given text to the displayed output box.
        The tag can be used to modify the text displayed.
        Tags are "normal" (default), "hint", "valid" and "invalid".
        """
        # Enable the output box and insert text
        self.output_box["state"] = "normal"
        self.output_box.insert(INSERT, text, tag)

        # Scroll to the bottom and disable the output box
        self.output_box.see(END)
        self.output_box["state"] = "disabled"


    # Button Functions

    def solve_btn(self):
        """
        A function to handle the user cliking on the solve button.
        Allows start/stop functionality depending on if the
        genetic algorithm is running
        """
        if self.ga_thread.is_alive():
            # GA running, stop the GA
            self.running_ga = False
            #self.output("\nStopped solving grid.\n\n")

        else:
            # Run the GA
            self.solve_grid()

    
    def solve_grid(self):
        """
        A function to handle the user clicking on the solve button to start.
        Checks user entry and begins the process for solving the grid
        """
        # Build grid class from user entry
        self.grid.user_rows.clear()
        self.grid.user_rows = self.get_user_rows()

        ## Hard coded grid for testing
        #rows = []
        ##Extreme 2
        #rows.append([0, 0, 0, 8, 1, 0, 3, 0, 0])
        #rows.append([8, 3, 0, 0, 0, 0, 0, 0, 0])
        #rows.append([0, 0, 0, 0, 0, 5, 4, 0, 1])
        #rows.append([7, 0, 0, 0, 0, 0, 0, 2, 9])
        #rows.append([0, 0, 0, 2, 5, 7, 0, 0, 0])
        #rows.append([5, 8, 0, 0, 0, 0, 0, 0, 3])
        #rows.append([2, 0, 5, 1, 0, 0, 0, 0, 0])
        #rows.append([0, 0, 0, 0, 0, 0, 0, 9, 4])
        #rows.append([0, 0, 3, 0, 7, 4, 0, 0, 0])
#
        #self.grid.user_rows = rows
        
        # Check user entry follows sudoku rules for duplicates
        if self.grid.check_user_grid():
            # Confirm user choice to continue
            #if user_confirm_continue():
            # Run GA
            self.running_ga = True
            self.ga_thread = threading.Thread(target=self.run_ga)
            self.ga_thread.daemon = True
            self.ga_thread.start()

        else: # Grid isn't valid, show message box to user
            pass

    def get_user_rows(self):
        """
        A function to read user entry and return it as a list
        """
        rows = []
        for ui_row in range(len(self.grid_ui)):
            this_row = []
            for cell_num in range(len(self.grid_ui[ui_row])):
                entry = self.grid_ui[ui_row][cell_num].get()
                if entry.isdigit():
                    this_row.append(int(entry))
                else:
                    this_row.append(0)
            rows.append(this_row)

        return rows  

    def run_ga(self):
        """
        A function to handle running the genetic algorithm to
        complete the grid
        """
        # Update solve and reset buttons and disable grid to prevent entry
        self.solve_btn["text"] = "STOP"
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                self.grid_ui[ui_row][cell_num]["state"] = "disabled"
        self.reset_btn["state"] = "disabled"

        self.output("Solving...\nPress 'STOP' to stop solving.\n\n")
        
        # Run the GA in its own thread
        solver = gsol.GridSolver(self.grid, self.output)
        solve_thread = threading.Thread(target=solver.run)
        solve_thread.daemon = True
        solve_thread.start()

        # Wait for the GA thread to finish itself or when stopped by user
        while solve_thread.is_alive():
            self.ui.update()
            if not self.running_ga:
                solver.thread_running = False
        
        # Update grid ui based on solution found
        # Re-enable the grid and reset Solve button
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                if solver.solved and self.grid.user_rows[ui_row][cell_num] > 0:#self.grid_ui[ui_row][cell].get().isdigit():
                    self.grid_ui[ui_row][cell_num]["disabledforeground"] = self.col_fg_dis_clue
                    # Testing hard coded grid
                    self.grid_ui[ui_row][cell_num]["state"] = "normal"
                    self.grid_ui[ui_row][cell_num].delete(0, END)
                    self.grid_ui[ui_row][cell_num].insert(0, self.grid.user_rows[ui_row][cell_num])
                    self.grid_ui[ui_row][cell_num]["state"] = "disabled"
                else:
                    self.grid_ui[ui_row][cell_num]["state"] = "normal"

        self.solve_btn["text"] = "START"
        self.reset_btn["state"] = "normal"
        
        # Set button states if solved
        if solver.solved:
            self.solve_btn["state"] = "disabled"
            self.show_sol_btn["state"] = "normal"
            self.show_hint_btn["state"] = "normal"
            self.valid_entry_btn["state"] = "normal"
            self.clear_entry_btn["state"] = "normal"

            # Output new instructions to user
            message = "Click 'Show Solution' to display the solution.\n"
            message += "Click 'Show Hint' to display a random cell solution.\n"
            message += "Enter some attempts and click 'Validate' to check if correct.\n"
            message += "Click 'Clear Entries' to remove values not part of the original puzzle.\n"
            message += "Click 'RESET GRID' to begin again.\n\n"
            self.output(message)
            
    def show_solution(self):
        """
        A function to handle the user clicking the
        Show Solution button and displaying the solution
        on the grid
        """
        # Update grid
        self.update_grid_solution_ui()
        #print("solution shown")
        self.output("Solution shown.\nClick 'RESET GRID' to begin again.\n")
        
        # Update button states
        self.solve_btn["state"] = "disabled"
        self.show_sol_btn["state"] = "disabled"
        self.show_hint_btn["state"] = "disabled"
        self.valid_entry_btn["state"] = "disabled"
        self.clear_entry_btn["state"] = "disabled"

    def update_grid_solution_ui(self):
        """
        A function to update the grid ui with the solution
        """
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                if self.grid.user_rows[ui_row][cell_num] == 0:
                    self.grid_ui[ui_row][cell_num]["state"] = "normal" # In case cell is disabled from hint
                    self.grid_ui[ui_row][cell_num].delete(0, END)
                    self.grid_ui[ui_row][cell_num].insert(0, self.grid.current_solution[ui_row][cell_num])
                    # Imitate an active cell while disabled
                    self.grid_ui[ui_row][cell_num]["disabledforeground"] = self.col_fg_en_norm
                    self.grid_ui[ui_row][cell_num]["disabledbackground"] = self.col_valid #self.col_bg_en_norm
                    self.grid_ui[ui_row][cell_num]["state"] = "disabled"

    def show_hint(self):
        """
        A function to handle the user clicking on the
        Hint button. Checks the displayed grid for unsolved
        cells and randomly fills one in.
        """
        # Create list of unsolved cells
        unsolved_cells = []
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                # Check cell has a value that is incorrect or is empty
                entry = self.grid_ui[ui_row][cell_num].get()
                if ((entry.isdigit()
                and not self.grid.user_rows[ui_row][cell_num] == int(entry)
                and not self.grid.current_solution[ui_row][cell_num]  == int(entry))
                or not entry.isdigit()):
                    unsolved_cells.append((ui_row, cell_num))
        
        # Proceed if valid list of cells created
        if unsolved_cells:
            # Randomly pick a cell from the list and fill it in
            random.shuffle(unsolved_cells)
            row = unsolved_cells[0][0]
            col = unsolved_cells[0][1]

            self.grid_ui[row][col].delete(0, END)
            self.grid_ui[row][col].insert(0, self.grid.current_solution[row][col])

            # Cell is completed so disable it
            self.grid_ui[row][col]["disabledbackground"] = self.col_hint
            self.grid_ui[row][col]["disabledforeground"] = self.col_fg_en_norm
            self.grid_ui[row][col]["state"] = "disabled"
            #print(f"Hint shown at row {row + 1}, cell {col + 1}")
            self.output("Hint", "hint")
            self.output(f" shown at row {row + 1}, column {col + 1}\n\n")
        else: # No valid cells found
            #print("No cells valid to provide hint")
            self.output("No hints available.\n\n")

    def validate_user_entry(self):
        """
        A function to handle the user clicking on the
        Validate button. Checks the displayed grid for
        entries that are not part of the initial clues
        and checks for correctness. Changes the cell
        background depending on correctness.
        """
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                # Check the cell has a value and not part of the initial clues
                entry = self.grid_ui[ui_row][cell_num].get()
                if (entry.isdigit()
                and not self.grid.user_rows[ui_row][cell_num] == int(entry)):
                    # Check value against cell and change background accordingly
                    if self.grid.current_solution[ui_row][cell_num] == int(entry):
                        # Correct background
                        self.grid_ui[ui_row][cell_num]["bg"] = self.col_valid
                    else:
                        # Incorrect background
                        self.grid_ui[ui_row][cell_num]["bg"] = self.col_invalid
        
        self.output("Entries validated.\n")
        self.output("Green", "valid")
        self.output(" = Correct\n")
        self.output("Red", "invalid")
        self.output(" = Wrong\n\n")


    def clear_entries(self):
        """
        A function to handle the user clicking on the
        Clear Entries button. Resets any cells that are
        not part of the initial clues.
        """
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                # Check the cell is not part of the initial clues
                entry = self.grid_ui[ui_row][cell_num].get()
                if not (entry.isdigit()
                and self.grid.user_rows[ui_row][cell_num] == int(entry)):
                    self.grid_ui[ui_row][cell_num]["state"] = "normal"
                    self.grid_ui[ui_row][cell_num].delete(0, END)
                    self.grid_ui[ui_row][cell_num]["bg"] = self.col_bg_en_norm

        self.output("All entries cleared.\n\n")

    def reset_grid(self):
        """
        A function to handle the user clicking on the
        RESET GRID button. Resets all elements back to
        initial run state.
        """
        # Reset grid
        for ui_row in range(len(self.grid_ui)):
            for cell_num in range(len(self.grid_ui[ui_row])):
                self.grid_ui[ui_row][cell_num]["state"] = "normal"
                self.grid_ui[ui_row][cell_num].delete(0, END)
                self.grid_ui[ui_row][cell_num]["fg"] = self.col_fg_en_norm
                self.grid_ui[ui_row][cell_num]["disabledforeground"] = self.col_fg_dis_norm
                self.grid_ui[ui_row][cell_num]["bg"] = self.col_bg_en_norm
                self.grid_ui[ui_row][cell_num]["disabledbackground"] = self.col_bg_dis_norm

        # Reset buttons
        self.solve_btn["state"] = "normal"
        self.show_sol_btn["state"] = "disabled"
        self.show_hint_btn["state"] = "disabled"
        self.valid_entry_btn["state"] = "disabled"
        self.clear_entry_btn["state"] = "disabled"

        # Reset output window
        self.init_output_box()
        

        






"""
A program to solve sudoku puzzles using genetic algorithm optimisation.

Employs a GUI to allow a user to enter an unsolved sudoku puzzle and run the
genetic algorithm to solve the puzzle. The solution can then be displayed 
to the user through the GUI. The user can also request hints or validate
their guesses to check for correctness against the solution.
"""
if __name__ == "__main__":
    
    # Create the GUI and start the program
    gui = GUI()
    gui.display_window()
