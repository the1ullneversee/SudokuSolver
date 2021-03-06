<h1> Sudoku Solver Approach.</h1>
<p>
The approach to building an algorithm for solving the sudoku, started by reading the section Contraction Satisfaction Problems from (Norvig, 2020).
</p>
<p>
From there I studied the different type of consistency types, Arc, Node, Path etc… Gaining an understanding of how sets of values, and states can be validated. Once that was understood, constraints were then looked at, to understand how constraints such as AllDiff, can effect the way numbers are tried within the Sudoku board. Finally, the back tracking search algorithm was studied from the book. This algorithm would form the basis of my work. 
</p>
<p>
The Sudoku Solver itself is broken down into 2 sections.
Firstly, I build a model of the board in memory which helps finding cells, units, and running algorithms on those cells and units. Next, I apply naked single search, and then a naked pair, locked pair search (Hobiger, 2021), to the board which helps by reducing the search space for any future searches. But what I found, is that for the majority of the sudoku puzzles, this was enough to solve the whole board by looping to find naked singles, setting the values, then applying it again, along with the naked pair/locked pair search. This would also invalidate any boards where there is a collision in a value being place in a cell, and it not being empty.
</p>
<p>
Once the search space has been reduced, I then use the back track search to either invalidate or solve the board. The Back Track Search uses recursive depth-first search to try out different missing values on available cells. The available cells each have missing values which are pre-calculated. As an optimisation, the queue which returns the next available cell, has a minimum function applied, which selects the next available cell with the least number of available numbers or missing numbers if you will. This greatly helps the algorithm, by failing faster, and not going as deep before an error state is found. 
</p>
<p>
Further optimisations could be made by including the naked single/pair search when doing the Back Track Search. Unfortunately, time did not permit the inclusion this.
The data structure’s used are a mix of lists, and dictionaries. I found that a list, performance wise was not producing any drawbacks. The only issue was membership discovery was slow when detecting missing numbers or updating other cells if they matched a certain index. For this, I used a dictionary to often save cells themselves, with an update vector to apply. Lastly, I found that reading the board into memory, and creating an OOP structure of the cells, units, and board, greatly helped the speed at which I could reference cells, reference units, and create helper functions. By creating a lot of the helper code, I found that I could try different approaches, quickly, and fail quickly without having to write lots and lots of code repeatedly.
</P>

![GUI](GUI.jpg)
![Complete](GUI-CompleteSudoku.jpg)
![GUI](https://user-images.githubusercontent.com/8123313/139666306-825b0ee8-263f-4e2c-948f-5dd633f22591.jpg)
