import pygame
from SudokuSolver import SudokuPuzzles
import numpy as np 


class GUI():
    def __init__(self):
        self.pygame = pygame
        self.pygame.font.init()
        self.bts = SudokuPuzzles(self,self.pygame)
        self.screen = pygame.display.set_mode((500,620))
        self.pygame.display.set_caption("Sudoku Solver!")
        # img = pygame.image.load('icon.png')
        # pygame.display.set_icon(img)
        self.directory = "sudoku\\data"
        self.puzzleFileNames = ["very_easy_puzzle.npy","easy_puzzle.npy","medium_puzzle.npy","hard_puzzle.npy"]
        self.puzzleSolutionNames = ["very_easy_solution.npy","easy_solution.npy","medium_solution.npy","hard_solution.npy"]
        self.mainSudokus = None
        self.diffIndex = 3
        self.mainSudokusSolved = None
        self.LoadPuzzles(self.diffIndex)
        self.sudoku = self.mainSudokus[0]
        
        self.puzzleIndex = 0
        self.x = 0
        self.y =0
        self.dif = 500/9
        self.val = 0

        # Load test fonts for future use
        self.font1 = self.pygame.font.SysFont("comicsans", 40)
        self.font2 = self.pygame.font.SysFont("comicsans", 20)
        self.RunRoutine()

    def LoadPuzzles(self,diffIndex):
        self.puzzleIndex = 0
        self.mainSudokus = np.load(f"{self.directory}\\{self.puzzleFileNames[diffIndex]}")
        self.mainSudokusSolved = np.load(f"{self.directory}\\{self.puzzleSolutionNames[diffIndex]}")
        print(f"{self.puzzleFileNames[diffIndex]} has been loaded into the variable sudoku")
        print(f"sudoku.shape: {self.mainSudokus.shape}, sudoku[0].shape: {self.mainSudokus[0].shape}, sudoku.dtype: {self.mainSudokus.dtype}")

    def get_cord(self,pos):
        global x
        self.x = pos[0]//self.dif
        global y
        self.y = pos[1]//self.dif

    def draw_box(self):
        for i in range(2):
            self.pygame.draw.line(self.screen, (255, 0, 0), (self.x * self.dif-3, (self.y + i)*self.dif), (self.x * self.dif + self.dif + 3, (self.y + i)*self.dif), 7)
            self.pygame.draw.line(self.screen, (255, 0, 0), ( (self.x + i)* self.dif, self.y * self.dif ), ((self.x + i) * self.dif, self.y * self.dif + self.dif), 7)  

    # Function to draw required lines for making Sudoku grid        
    def draw(self):
        # Draw the lines
        for i in range (9):
            for j in range (9):
                if self.sudoku[j][i]!= 0:
                    # Fill blue color in already numbered grid
                    self.pygame.draw.rect(self.screen, (0, 153, 153), (i * self.dif, j * self.dif, self.dif + 1, self.dif + 1))
    
                    # Fill grid with default numbers specified
                    text1 = self.font1.render(str(self.sudoku[j][i]), 1, (0, 0, 0))
                    self.screen.blit(text1, (i * self.dif + 15, j * self.dif + 15))
        # Draw lines horizontally and verticallyto form grid          
        for i in range(10):
            if i % 3 == 0 :
                thick = 7
            else:
                thick = 1
            self.pygame.draw.line(self.screen, (0, 0, 0), (0, i * self.dif), (500, i * self.dif), thick)
            self.pygame.draw.line(self.screen, (0, 0, 0), (i * self.dif, 0), (i * self.dif, 500), thick)

    # Fill value entered in cell     
    def draw_val(self,val):
        text1 = self.font1.render(str(val), 1, (0, 0, 0))
        self.screen.blit(text1, (self.x * self.dif + 15, self.y * self.dif + 15))   

    # Raise error when wrong value entered
    def raise_error1(self):
        text1 = self.font1.render("WRONG !!!", 1, (0, 0, 0))
        self.screen.blit(text1, (20, 570)) 
    def raise_error2(self):
        text1 = self.font1.render("Wrong !!! Not a valid Key", 1, (0, 0, 0))
        self.screen.blit(text1, (20, 570))
     # Raise error when wrong value entered
    def raise_error3(self):
        text1 = self.font1.render("Board is invalid!", 1, (0, 0, 0))
        self.screen.blit(text1, (20, 580))  

    # Display instruction for the game
    def instruction(self):
        text0 = self.font2.render(f"Puzzle {self.puzzleIndex +1} of {self.puzzleFileNames[self.diffIndex]}", 1, (0, 0, 0))
        text1 = self.font2.render("PRESS D TO SHOW NEXT SUDOKU", 1, (0, 0, 0))
        text2 = self.font2.render("ENTER VALUES AND PRESS ENTER TO VISUALIZE", 1, (0, 0, 0))
        self.screen.blit(text0, (20, 520))   
        self.screen.blit(text1, (20, 540))       
        self.screen.blit(text2, (20, 560))
    
    # Display options when solved
    def result(self):
        text1 = self.font1.render("FINISHED PRESS R or D", 1, (0, 0, 0))
        self.screen.blit(text1, (20, 570)) 

    def RunRoutine(self):
        print(self.mainSudokusSolved[self.puzzleIndex])
        run = True
        flag1 = 0
        flag2 = 0
        rs = 0
        error = 0
        # The loop thats keep the window running
        while run:
            
            # White color background
            self.screen.fill((255, 255, 255))
            # Loop through the events stored in event.get()
            for event in self.pygame.event.get():
                # Quit the game window
                if event.type == self.pygame.QUIT:
                    run = False 
                # Get the mouse position to insert number   
                if event.type == self.pygame.MOUSEBUTTONDOWN:
                    flag1 = 1
                    pos = self.pygame.mouse.get_pos()
                    self.get_cord(pos)
                # Get the number to be inserted if key pressed   
                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_LEFT:
                        self.x-= 1
                        flag1 = 1
                    if event.key == self.pygame.K_RIGHT:
                        self.x+= 1
                        flag1 = 1
                    if event.key == self.pygame.K_UP:
                        self.y-= 1
                        flag1 = 1
                    if event.key == self.pygame.K_DOWN:
                        self.y+= 1
                        flag1 = 1   
                    if event.key == self.pygame.K_1:
                        self.val = 1
                    if event.key == self.pygame.K_2:
                        self.val = 2   
                    if event.key == self.pygame.K_3:
                        self.val = 3
                    if event.key == self.pygame.K_4:
                        self.val = 4
                    if event.key == self.pygame.K_5:
                        self.val = 5
                    if event.key == self.pygame.K_6:
                        self.val = 6
                    if event.key == self.pygame.K_7:
                        self.val = 7
                    if event.key == self.pygame.K_8:
                        self.val = 8
                    if event.key == self.pygame.K_9:
                        self.val = 9 
                    if event.key == self.pygame.K_RETURN:
                        flag2 = 1  
                    if event.key == pygame.K_d:
                        self.puzzleIndex += 1
                        if self.puzzleIndex > 14:
                            self.diffIndex+=1
                            self.LoadPuzzles(self.diffIndex)
                        rs = 0
                        error = 0
                        flag2 = 0
                        self.sudoku = self.mainSudokus[self.puzzleIndex]
            if flag2 == 1:
                ret = self.bts.BackTrackingSearch(self.sudoku)
                
                if not ret:
                    error = 3
                    print("Bad Puzzle")
                flag2 = 0   
            if self.val != 0:           
                self.draw_val(val)
                val = 0   
            
            if error == 3:
                self.raise_error3()
            if rs == 1:
                self.result()       
            self.draw() 
            if flag1 == 1:
                self.draw_box()      
            self.instruction()   
        
            # Update window
            self.pygame.display.update() 
        # Quit pygame window   
        self.pygame.quit()
gui = GUI()