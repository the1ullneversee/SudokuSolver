from typing import Deque
import numpy as np
import math
import time
import random
import copy

class Cell():
    def __init__(self, index, value,emptyNeighbours,xDomain,yDomain, unit, unitDomain):
        self.index = index
        self.emptyNeighbours = emptyNeighbours
        self.value = value
        self.xDomain = xDomain.copy()
        self.yDomain = yDomain.copy()
        self.unitDomain = unitDomain.copy()
        self.domain = set.union(set(self.xDomain.values()), set(self.yDomain.values()),set(self.unitDomain.values()))
        self.unit = unit
        #self.potentials = [x for x in range(1,10) if x not in self.unitDomain.values() or x not in self.xDomain.values() or x not in self.yDomain.values()]
        self.missing = [x for x in range(1,10) if x not in self.unitDomain.values() and x not in self.xDomain.values() and x not in self.yDomain.values()]
        self.tried = []
        self.uniqueValue = None
    
    def IsEmpty(self):
        return self.value == 0

    def IncrementEmpty(self):
        self.emptyNeighbours += 1
    
    def GetEmpty(self):
        return self.emptyNeighbours
    
    def GetIndex(self):
        return self.index
    
    def __str__(self):
        return f"[{self.index}] with {self.emptyNeighbours} neighbours, and {self.domain} domain"

    def __eq__(self,other):
        return type(self) == type(other)
        return self.emptyNeighbours == other.emptyNeighbours
    
    def __lt__(self,other):
        return len(self.missing) < len(other.missing)
        #return self.emptyNeighbours < other.emptyNeighbours
    
    def __gt__(self,other):
        return len(self.missing) > len(other.missing)
        #return self.emptyNeighbours > other.emptyNeighbours
    
    def TriggerMissingCalculation(self):
        self.missing = [x for x in range(1,10) if x not in self.unitDomain.values() and x not in self.xDomain.values() and x not in self.yDomain.values()]

    def GetMissing(self):
        return self.missing
        #return [x for x in range(1,10) if x not in self.unitDomain.values() and x not in self.xDomain.values() and x not in self.yDomain.values()]
    
    def RemoveValue(self,value):
        self.missing.remove(value)
    
    def GetTried(self):
        return self.tried

    def GetXDomain(self):
        return [x for x in self.xDomain.values() if x != 0]

    def GetYDomain(self):
        return [y for y in self.yDomain.values() if y != 0]

    def GetUnitDomain(self):
        return [u for u in self.unitDomain.values() if u != 0]

class Unit():
    def __init__(self, unitX, unitY):
        self.unitX = unitX
        self.unitY = unitY
        self.cells = []
    
    def AddCell(self, cell):
        self.cells.append(cell)

    def PrintCells(self):
        str = ""
        for cell in self.cells:
            str += f"{cell.index}"
        return str
    
    def __str__(self):
        return f"Unit {self.unitY},{self.unitX}\n" + self.PrintCells() + "\n"

class Board():
    def __init__(self,rows, cols,input):
        self.master = input
        self.rows = rows
        self.cols = cols
        self.cells = None
        self.unassigned = None
        self.missing = None
        self.countMissing = None
        self.units = None
        self.InitBoard()
        self.valid = True
        self.queue = None
    
    def InitBoard(self):
        unitx = 1
        unity = 1
        defaultDomain = [1,2,3,4,5,6,7,8,9]
        self.cells = []
        self.missing = []
        yDomains = [self.GenerateYDomain(x) for x in range(0,9)]
        xDomains = [self.GenerateXDomain(y) for y in range(0,9)]
        for y in range(0,9):
            domain = yDomains[y]
            for i in range(1,10):
                if i not in domain.values():
                    self.missing.append(i)
        unitDomains = {}
        x = 0
        y = 0
        self.units = {}
        for y in range(1,4):
            for x in range(1,4):
                self.units[(x,y)] = Unit(x,y)
        for y,e in enumerate(self.master):
            if y != 0 and y%3 ==0:
                unity += 1
            for x,d in enumerate(e):
                if x!= 0 and x%3 == 0:
                    unitx += 1
                unit = (unitx,unity)
                if unit not in unitDomains:
                    cords = self.GenerateSquare((y,x))
                    #remove cords on the x and y plane
                    values = self.GenerateUnitDomain(cords)
                    unitDomains[unit] = values
                cell = Cell(index=(y,x),value=d,emptyNeighbours=0,xDomain=xDomains[y],yDomain=yDomains[x],unit=unit, unitDomain=unitDomains[unit])
                self.units[(unitx,unity)].AddCell(cell)
                self.cells.append(cell)
            unitx =1
        self.GenerateEmptyCellRelations()

    #generates the domain on the Y axis
    def GenerateYDomain(self,x):
        verticalValues = {}
        for y in range(0,9):
            verticalValues[(y,x)] = self.master[y][x]
            #verticalValues.append(self.master[y][x])
        return verticalValues
    
    def GenerateYDomainValues(self,x):
        verticalValues = []
        for y in range(0,9):
            if self.master[y][x] != 0:
                verticalValues.append(self.master[y][x])
            #verticalValues.append(self.master[y][x])
        return verticalValues

    #Generates the coordinates for any unit on the board, given a set of coordinates.
    def GenerateSquare(self,index):
        numMajorRows = 3
        numMajorCols = 3
        width = 3
        x = index[1]+1
        y = index[0]+1
        placement = []
        placement.append(index)

        e = 0
        t = x%3
        a = x
        if t != 0:
            e = 3-t
            a = e+x
        xSquare = (int)(a/3)

        t = y%3
        a = y
        if t != 0:
            e = 3-t
            a = e+y
        ySquare = (int)(a/3)
        #print(f"coordinates ({x-1},{y-1}) are in box x {xSquare} by y {ySquare}")
        upperBoundX = (xSquare) * 3
        lowerBoundX = upperBoundX - 3
        upperBoundY = (ySquare) * 3
        lowerBoundY = upperBoundY - 3
        square = [(i,j) for i in range(lowerBoundY,upperBoundY) for j in range(lowerBoundX,upperBoundX)]
        #print(square)
        return square


    #generates the domain for X
    def GenerateXDomain(self,y):
        values = {}
        for x in range(0,9):
            values[(y,x)] = self.master[y][x]
            #verticalValues.append(self.master[y][x])
        return values
    
    def GenerateXDomainValues(self,y):
        values = []
        for x in range(0,9):
            if self.master[y][x] != 0:
                values.append(self.master[y][x])
            #verticalValues.append(self.master[y][x])
        return values
    
    #generates the unit domain for the coordinates given
    def GenerateUnitDomain(self, coords):
        values = {}
        for position in coords:
             values[position] = self.master[position[0]][position[1]]
            #values.append(self.master[position[1]][position[0]])
        return values
    
    #generates the unit domain for the coordinates given
    def GenerateUnitDomainValues(self, coords):
        values = []
        for position in coords:
            if self.master[position[0]][position[1]] != 0:
             values.append(self.master[position[0]][position[1]])
            #values.append(self.master[position[1]][position[0]])
        return values

    #This function is responsible for generating the empty cell relations for each cell in the sudoku grid. It essentiall creates a graph between each empty cell and a cell it influences. 
    def GenerateEmptyCellRelations(self):

        for unit in self.units.values():
            for cell in unit.cells:
            #for cell in self.cells:
                #if cell.IsEmpty():
                #print(cell.index)
                emptyNeigBourIndex = []
                ##use the values for gettting out of the dictionary.
                if 0 in cell.xDomain.values():
                    for x in cell.xDomain:
                        if x != cell.index and cell.xDomain[x] == 0:
                            emptyNeigBourIndex.append(x)
                if 0 in cell.yDomain.values():
                    for y in cell.yDomain:
                        if y != cell.index and cell.yDomain[y] == 0 and y not in emptyNeigBourIndex:
                            emptyNeigBourIndex.append(y)
                    
                #number of unit cells which also do not appear in empty index from the X and Y domains.
                units = [u for u in cell.unitDomain if cell.unitDomain[u] == 0 and u not in emptyNeigBourIndex and u != cell.index]
                cell.emptyNeighbours = len(units) + len(emptyNeigBourIndex)
                # domains = [set(cell.GetXDomain()),set(cell.GetYDomain()),set(cell.GetUnitDomain())]
                # diff = set.symmetric_difference(domains[0],domains[1])
                # diff = set.symmetric_difference(diff,domains[2])
                # cell.uniqueValue = diff
    
    def GenerateUnassignedCellReference(self):
        self.unassigned = []
        for cell in self.cells:
            if cell.IsEmpty():
                self.unassigned.append(cell)
    
    def GenerateQueue(self):
        #first look for the lowest neighbours
        #add to a stack so we can work our way through without retrying in a loop
        queue = []
        for unit in self.units.values():
            for tCell in unit.cells:
                if tCell.IsEmpty():
                    queue.append(tCell)
        
        return queue

    #Generates a list of empty boxes in the sudoku board
    def GetUnassigned(self):
        return self.unassigned
        
    def GenerateUnassigned(self):
        unassigned = []
        for unit in self.units.values():
            for cell in unit.cells:
                if cell.IsEmpty():
                    unassigned.append(cell)
        self.unassigned = unassigned

    def AddUnassigned(self, val):
        self.unassigned.append(val)

    def RemoveCell(self,val):
        self.unassigned = [s for s in self.unassigned if s.index != val.index]

    #Sets the cell value with the function arguement, and also triggers a contraint propagation on the newly filled value, removing it from neighbowur domains.
    def SetCell(self, cell, value):
        value = np.int8(value)
        
        if self.master[cell.index[0]][cell.index[1]] != 0:
            return None #ValueError(f"Not empty! {cell.index}")
        state = copy.deepcopy(self)
        state.queue = [q for q in state.queue if q.index != cell.index]
        state.master[cell.index[0]][cell.index[1]] = value
        unit = state.units[cell.unit]
        #update all other values that relate to the cell being updated
        for unit in state.units.values():
            for oCell in unit.cells:
                if oCell.index == cell.index:
                    oCell.tried.append(value)
                    oCell.value = np.int8(value)
                    if value in oCell.missing:
                        oCell.missing.remove(value)
                    continue
                
                if cell.index in oCell.xDomain:
                    oCell.xDomain[cell.index] = value
                    oCell.TriggerMissingCalculation()
                    if cell.IsEmpty():
                        oCell.emptyNeighbours -= 1
                if cell.index in oCell.yDomain:
                    oCell.yDomain[cell.index] = value
                    oCell.TriggerMissingCalculation()
                    if cell.IsEmpty():
                        oCell.emptyNeighbours -= 1
                if cell.unit == oCell.unit:
                    oCell.unitDomain[cell.index] = value
                    oCell.TriggerMissingCalculation()
                    if cell.index not in oCell.yDomain and cell.index not in oCell.xDomain:
                        if cell.IsEmpty():
                            oCell.emptyNeighbours -= 1
            
        return state

    #Sets the cell value with the function arguement, and also triggers a contraint propagation on the newly filled value, removing it from neighbour domains.
    def RemoveCellValue(self, cell, value):
        #print(f"removing cell [{cell.index[0]},{cell.index[1]}] with {value}")
        self.master[cell.index[0]][cell.index[1]] = 0
        unit = self.units[cell.unit]
        for tCell in unit.cells:
            if tCell.index == cell.index:
                tCell.value = 0
                tCell.missing.append(value)
                break
        #cell.missing.append(value)
        #update all other values that relate to the cell being updated
        for unit in self.units.values():
            for oCell in unit.cells:
                if cell.index in oCell.xDomain:
                    oCell.xDomain[cell.index] = 0
                    oCell.TriggerMissingCalculation()
                if cell.index in oCell.yDomain:
                    oCell.yDomain[cell.index] = 0
                    oCell.TriggerMissingCalculation()
                if cell.unit == oCell.unit:
                    oCell.unitDomain[cell.index] = 0
                    oCell.TriggerMissingCalculation()

    def IsGoal(self):
        values = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
        
        for unit in self.units.values():
            for tCell in unit.cells:
                if tCell.value == 0:
                    return False
                values[tCell.value] += 1
                #diff = set.difference(values,set(tCell.GetYDomain()))
        if len([i for i in range(1,10) if values[i] != 9]) != 0:
            return False
        return True
            
    def GetNextQueueItem(self):
        if len(self.queue) > 0:
            return min(self.queue)
        return None

    
    def __str__(self):
        return np.array2string(self.master)

class SudokuPuzzles:

    directory = "sudoku\\data"
    puzzleFileNames = ["very_easy_puzzle.npy","easy_puzzle.npy","medium_puzzle.npy","hard_puzzle.npy"]
    puzzleSolutionNames = ["very_easy_solution.npy","easy_solution.npy","medium_solution.npy","hard_solution.npy"]

    def __init__(self,gui,pygame):
        self.mainBoard = None
        self.gui = gui
        self.pygame = pygame
    
    #check that the number can fit
    #We will need to check horizontal, vertical, and locally in the unit.
    def ValidAssignment(self,sudoku,value,index):
        #print(f"Checking {value} placement at {index}")
        #first check the placement is actuall valid!
        if(sudoku[index[0]][index[1]] != 0):
            #print("Invalid")
            return False 
        
        valid = True
        x = index[1]
        y = index[0]

        #generates the local unit coordinates
        unit = self.GenerateSquare(index)
        #keep hold of what cells we have searched so far
        searched = set()
        #horizontal
        searched.add(index)

        #essentially we search in 4 directions at once! From X back and front, and Y up and down.
        #we need index for left minus right plus up minus and down plus!
        ix = x
        jx = x
        iy = y
        jy = y
        #print(sudoku)
        #y = sudoku[y][0:]
        while(ix >= 0 or jx < 9 or iy >= 0 or jy <9):
            ix -= 1
            jx += 1
            iy -= 1
            jy += 1
            if ix >= 0:
                searched.add((y,ix))
                if sudoku[y][ix] == value:
                    #print(f"({y},{ix}) Not Valid")
                    return False
            if jx <= 8:
                searched.add((y,jx))
                if sudoku[y][jx] == value:
                    #print(f"({y},{jx}) Not Valid")
                    return False
            if iy >= 0:
                searched.add((iy,x))
                if sudoku[iy][x] == value:
                    #print(f"({iy},{x}) Not Valid")
                    return False
            if jy <= 8:
                searched.add((jy,x))
                if sudoku[jy][x] == value:
                    #print(f"({jy},{x}) Not Valid")
                    return False
        if [i for i in unit if i not in searched and sudoku[i[0]][i[1]] == value]:
            valid = False
        return valid

    #Use set() to remove duplicates if all values are hashable:
    def ValidateValues(self,values):
        #print(values)
        #we remove zeros because there can be duplicate 0's in the row/column!
        values = [a for a in values if a != 0]
        #values = np.delete(values,np.where(values.any() == 0))
        if len(values) != len(set(values)):
            return False
        return True

    #Use set() to remove duplicates if all values are hashable:
    def ValidateUnit(self,board, unit):
        #print(unit)
        values = []
        for position in unit:
            #print(board.master[position[1]][position[0]])
            values.append(board.master[position[1]][position[0]])
        values = [a for a in values if a != 0]
        if len(values) != len(set(values)):
            return False
        return True

    def ValidateBoard(self,board):
        x = 1

        #validate horizontal values
        for y,e in enumerate(board.master):
            if not self.ValidateValues(e):
                #print(f"Invalid state detected on the horizontal values {e}")
                return False

        #validate verical values
        for x in range(0,9):
            verticalValues = []
            for y in range(0,9):
                verticalValues.append(board.master[y][x])
            if not self.ValidateValues(verticalValues):
                #print(f"Invalid state detected on the verical values {verticalValues}")
                return False
        
        #validate each unit
        for y in range(1,4):
            unity = y
            for x in range(1,4):
                unitx = x
                unitCoordinates = board.GenerateSquare((unity,unitx))
                #print(unitCoordinates)
                if not self.ValidateUnit(board,unitCoordinates):
                    #print(f"Invalid state detected in the unit values {unitCoordinates}")
                    return False

        for cell in board.GetUnassigned():
            if len(cell.GetMissing()) == 0:
                #If the cell has no missing values in its domain, but is itself empty, then the board must be in an invalid state.
                return False
            
        return True

    def DetectEmptyInUnit(self,board, unit):
        values = []
        for position in unit:
            #print(board.master[position[1]][position[0]])
            values.append(board[position[1]][position[0]])
        values = [a for a in values if a == 0]
        return len(values)-1

    def CheckDomainContraint(self,assignment,value):
        matchesFound = 0
        for unit in assignment.units.values():
            domain = unit.cells[0].GetUnitDomain()
            #print(f"{unit.cells[0].unit} has {domain} domain")
            if value in domain:
                matchesFound += 1
        #print(f"{value} has {matchesFound} matches")
        if matchesFound > 9:
            print(assignment)
            #print("Error state found!")
            return False
        return True

    def GetAvailableLocations(self,assignment,value):
        pos = []
        values = [1,2,3,4,5,6,7,8,9]
        for unit in assignment.units.values():
            domain = unit.cells[0].GetUnitDomain()
            diff = domain - values
            if value not in domain:
                for cell in unit.cells:
                    if cell.IsEmpty():
                        if value not in cell.xDomain.values() and value not in cell.yDomain.values():
                            pos.append(cell)
        return pos

    def GetMissingNumbers(self,assignment):
        diffs = []
        values = {1,2,3,4,5,6,7,8,9}
        for unit in assignment.units.values():
            domain = set(unit.cells[0].GetUnitDomain())
            diff = set.difference(values,domain)
            if len(diff) != 0:
                diffs += domain
                #diffs = set.union(diffs,diff)
            #diffs.append(diff)
        return diffs

    def BackTrack(self,assignment,it):
        
        #unassigned is generated before the start of back tracking, but looking at the empty cells.
        #queue is ordered by lowest amount of neighbours
        p = assignment.GetNextQueueItem()

        if p:
            #search through all missing values
            self.pygame.event.pump()
            self.gui.screen.fill((255, 255, 255))
            self.gui.draw()
            self.gui.draw_box()
            self.pygame.display.update()
            self.pygame.time.delay(20)
            for val in p.missing:
                it += 1
                #check that the placement does not actually cause any domain related consistency errors
                if len([s for s in assignment.queue if len(s.missing) == 0]) > 0:
                    return None
                
                #set the cell with the value, and update the domains of neighbouring cells
                newState = assignment.SetCell(p,val)
                self.gui.sudoku = newState.master
                
                if newState.IsGoal():
                    return newState
                
                #try another place/value
                deepState = self.BackTrack(newState,it)
                if deepState is not None and deepState.IsGoal():
                    #success
                    return deepState
            return None
        
    def GenerateUnitValues(self,board, unit):
        for unit in board.units:
            domain = []
            for cell in unit.cells:
                domain.append(cell.GetMissing())
        return True

    def ApplyNakedPairOld(self,board):
        pairFound = False
        searchSpace = board.units
        unitX = 1
        unitY = 1
        i = 0
        j = 0
        #just to set off the loop properly
        tup = ()
        cell = searchSpace[(unitX,unitY)].cells[j]
        while(cell.index != (8,8) and not pairFound):
            for unitY in range(1,4):
                #for each unit we detect if there are naked pairs
                for unitX in range(1,4):
                    pair = {}
                    unit = searchSpace[(unitX,unitY)].cells
                    for cell in unit:
                        if cell.IsEmpty():
                            if len(cell.missing) == 2:
                                cellAsSet = set(cell.missing)
                                cellAsKey = str(cellAsSet)
                                if cellAsKey not in pair.keys():
                                    pair[cellAsKey] = cell
                                else:
                                    pair[cellAsKey] = (pair[cellAsKey],cell)
                    
                    for p in pair.values(): 
                        self.UpdateUnitMissingValues(board=board,unit=(unitX,unitY),oCell=p,value=cell.value)
                        self.UpdateRelativeXandYMissingValues(board=board,unit=(unitX,unitY),oCell=p,value=cell.value)
                #update the rest

    def ApplyNakedPair(self,board):
        print(board)
        pairFound = False
        searchSpace = board.units
        unitX = 1
        unitY = 1
        i = 0
        j = 0
        #just to set off the loop properly
        tup = ()
        cell = searchSpace[(unitX,unitY)].cells[j]
        missingCell = []
        nakedPair = []
        rowPair = {}
        lockedPair = []
        columnPair = {}
        for unit in board.units.values():
            for cell in unit.cells:
                if cell.IsEmpty():
                    #print(f"{cell.index} missing {cell.missing}")
                    if len(cell.missing) == 2:
                        missingCell.append(cell)
        pair = {}
        for m in missingCell:
            m.missing.sort()
            if f"{m.missing}" not in pair:
                pair[f"{m.missing}"] = [m]
                #print(m.missing)
            else:
                for cell in pair[f"{m.missing}"]:
                    #print(f"comparing {cell.index} with {m.index} because {cell.missing} == {m.missing}")
                    if cell.unit == m.unit and cell.index[0] == m.index[0] and cell.index[1] == m.index[1]:
                        #print(f"naked pair {cell.index} {m.index} share {cell.missing} and {m.missing}")
                        #nakedPair.add((cell,m))
                        self.UpdateRelativeXandYMissingValues(board,cell.unit,(cell,m))
                    elif cell.index[0] == m.index[0] or cell.index[1] == m.index[1] and cell.unit == m.unit:
                        #print(f"Locked Pair {cell.index} {m.index} share {cell.missing} and {m.missing}")
                        #lockedPair.add((cell,m))
                        self.UpdateUnitMissingValues(board,cell.unit,(cell,m))
                        self.UpdateRelativeXandYMissingValues(board,cell.unit,(cell,m))
                    elif cell.index[0] == m.index[0] or cell.index[1] == m.index[1]:
                        #print(f"naked pair with same index relation {cell.index} {m.index} share {cell.missing} and {m.missing}")
                        #nakedPair.add((cell,m))
                        self.UpdateRelativeXandYMissingValues(board,cell.unit,(cell,m))
                    elif cell.unit == m.unit:
                        #print(f"naked pair with same domain {cell.index} {m.index} share {cell.missing} and {m.missing}")
                        self.UpdateUnitMissingValues(board,cell.unit,(cell,m))
                    #else:
                        #print("No relation")
                pair[f"{m.missing}"].append(cell)
        print("Done")

    def UpdateUnitMissingValues(self,board,unit,cells):
        for cell in board.units[unit].cells:
            #don't update the cell that generated the double pair
            if cell.index != cells[0].index and cell.index != cells[1].index:
                #print(cell.missing)
                if cell.IsEmpty():
                        for val in cells[0].missing:
                            if val in cell.missing:
                                cell.missing.remove(val)

    def UpdateRelativeXandYMissingValues(self,board,unit,cells):
        targetSingleIndex = 0
        if cells[0].index[0] == cells[1].index[0]:
            targetSingleIndex = ("x",cells[0].index[0])
        elif cells[0].index[1] == cells[1].index[1]:
            targetSingleIndex = ("y",cells[0].index[1])
        else:
            return

        units = board.units
        for unit in units.values():
            for cell in unit.cells:
                if cell.index != cells[0].index and cell.index != cells[1].index:
                    if cell.IsEmpty():
                        if targetSingleIndex[0] == "y":
                            if cell.index[1] == targetSingleIndex[1]:
                                for val in cells[0].missing:
                                    if val in cell.missing:
                                        cell.missing.remove(val)
                        if targetSingleIndex[0] == "x":
                            if cell.index[0] == targetSingleIndex[1]:
                                for val in cells[0].missing:
                                    if val in cell.missing:
                                        cell.missing.remove(val)
                            
                                print(cell.index)


    def FindUniqueDomainCells(self,board):
        uniqueValueCells = []
        #print(board)
        for unit in board.units.values():
            uniqueVals = {1:(0,),2:(0,),3:(0,),4:(0,),5:(0,),6:(0,),7:(0,),8:(0,),9:(0,)}
            #go through all the units, and mark off the missing values. 
            for cell in unit.cells:
                if cell.IsEmpty():
                    for i in cell.GetMissing():
                        uniqueVals[i] = (uniqueVals[i][0]+1,cell)
                #values = set.symmetric_difference(values,s)
            for key in uniqueVals.keys():
                if uniqueVals[key][0] == 1:
                    c = uniqueVals[key]
                    #print(f"{unit} has 1 space for number {key} at {c[1].index}")
                    uniqueValueCells.append((c[1],key))
        return uniqueValueCells
            

    def BackTrackingSearch(self,sudoku):
        start = time.process_time()
        negativeBoard = array = np.full(sudoku.shape,-1)
        self.mainBoard = Board(9,9,sudoku)
        #next we get all the unassigned cells on the board, which have elements such as value, index, and emptyneighbours to help.
        self.mainBoard.GenerateUnassignedCellReference()
        self.mainBoard.queue = self.mainBoard.GetUnassigned()

        #Then we validate the board, using a constraint search to rule out any invalid columns, rows, or units.
        if not self.ValidateBoard(self.mainBoard):
            return False
        searchSpace = 0

        #use CSP with consistency search of naked single
        cells = self.FindUniqueDomainCells(board=self.mainBoard)
        while(len(cells) != 0):
            #tuple will come back
            for cell in cells:
                #mainBoard = self.SetCell(mainBoard,cell)
                self.mainBoard = self.mainBoard.SetCell(cell[0],cell[1])
                self.gui.sudoku[cell[0].index[0]][cell[0].index[1]] = cell[1]
                self.pygame.event.pump()
                
                self.gui.screen.fill((255, 255, 255))
                self.gui.draw()
                self.gui.draw_box()
                self.pygame.display.update()
                self.pygame.time.delay(20)
                
                #mainBoard = mainBoard.SetCell(cell[0],cell[1])
                if self.mainBoard is None:
                    return False
                    if not mainBoard.ValidateBoard(mainBoard):
                        return False
                #print(mainBoard)
                #remove this cell as unassigned.
                cells = [c for c in cells if c[0].index != cell[0].index]
                #print(cells)
                searchSpace += 1
            #use CSP with consistency search of naked pair, or locked pair. Reduces the domain!
            self.ApplyNakedPair(board=self.mainBoard)
            #use CSP with consistency search of naked single
            cells = self.FindUniqueDomainCells(board=self.mainBoard)

        #Are we in a valid state?
        if self.mainBoard.IsGoal():
            return True

        #check if there are any cells with no missing items, that cannot happen to go forward.
        for q in self.mainBoard.queue:
            if len(q.missing) == 0:
                return False

        it = 0
        end = time.process_time()
        print(f"reduced state space by {searchSpace} took {end-start}")
        #call the recursive back track search
        result = self.BackTrack(self.mainBoard,it)
        if result:
            return True
        return False
    
    def ReturnPuzzle(self, difficulty,puzzleIndex):
        mainSudoku = np.load(f"sudoku/data/{self.puzzleFileNames[difficulty]}")
        print(f"{self.puzzleFileNames[difficulty]} has been loaded into the variable sudoku")
        print(f"sudoku.shape: {mainSudoku.shape}, sudoku[0].shape: {mainSudoku[0].shape}, sudoku.dtype: {mainSudoku.dtype}")

        return (mainSudoku[puzzleIndex],self.puzzleFileNames[difficulty])

    def RunAllTests(self):
        timings = []
        
        for j in range(0,4):
            mainSudoku = np.load(f"OMITTED//{self.puzzleFileNames[j]}")
            mainSudokuSolved = np.load(f"OMITTED//{self.puzzleSolutionNames[j]}")
            print(f"{self.puzzleFileNames[j]} has been loaded into the variable sudoku")
            print(f"sudoku.shape: {mainSudoku.shape}, sudoku[0].shape: {mainSudoku[0].shape}, sudoku.dtype: {mainSudoku.dtype}")
            
            for i in range(0,mainSudoku.shape[0]):
                #self.gui = GUI(mainSudoku[i],self.puzzleFileNames[j])
                #self.gui.Update()
                print("=============================")
                print(f"Solving puzzle {i}")
                start = time.process_time()
                print(mainSudoku[i])
                solved = self.BackTrackingSearch(sudoku=mainSudoku[i])
                end = time.process_time()
                print(f"took {end-start}s to solve puzzle {i} of {self.puzzleFileNames[j]}")
                timings.append(f"took {end-start}s to solve puzzle {i} of {self.puzzleFileNames[j]}")
                if type(solved) == bool:
                    print("ERROR!")
                    break
                print("Generated Solution")
                print(solved)
                print("Known Solution")
                print(mainSudokuSolved[i])
                #print("Comparison")
                values = mainSudokuSolved[i].all() == solved.all()
                #print(values)
                if values.any() == False:
                    print("Puzzle Solving Failed")
                    #print(f"{puzzleFileNames[j]} Sudoku {i} Not Solved Correctly!")
                    #print(mainSudokuSolved[i])
                    #print(solved)
                    #print(values)
                    #break
                else:
                    print("Puzzle Solving Passed")
                print("=============================")

        for t in timings:
            print("========")
            print(t)
            print("========")