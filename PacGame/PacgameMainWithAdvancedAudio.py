import tkinter as tk
import time
import random
import asyncio
import collections
import threading
import platform
import pygame #exclusive to this version!

#TODO
#Allow users to choose enemy and objective amount
    #Create entry for both then connect it to values in the GenerateMap function

if platform.system() == "Windows":
    import winsound #the only built in sound playing plugin. Requires windows operating system.

    # Initialize pygame mixer once in the main program
    pygame.mixer.init()
else:
    print("Running on os " + platform.system())

root = tk.Tk()
if platform.system() == "Windows":
    root.iconphoto(False,tk.PhotoImage(file="nuteralEmojiIcon.png")) #icon creation, only will work on PCs
root.geometry("400x400")

Version = "v0.7 Pygame"
root.title("PacGame " + Version)
GridY = 0
GridX = 0
CurrentMap = {
    "SizeX": 0, #15
    "SizeY": 0, #13
    "Spaces": {},
    "Walls": [],
    "Enemies": {},
    "Objectives": {},
    "GoalSpace": None,
    "TKGoalSpace": None,
    "CanWin": False
}
MoveCD = False
RegenCD = False
PlayerWin = False
CloseGame = False
KillPlayer = False
ResetMap = False

#items
DynamiteToggled = False
globaldynamite = 3
DynamiteLeft = 3

BaseFrame = tk.Frame(root)
BaseFrame.grid()
GameFrame = tk.Frame(root)
GameFrame.grid(column=0,row=1)

def CloseGameFunc(ThyRoot):
    global CloseGame
    global CurrentMap
    
    CloseGame = True
    ThyRoot.destroy()

button = tk.Button(BaseFrame, text = "Quit", command = lambda: CloseGameFunc(root))
TopLabel = tk.Label(BaseFrame, text = "Welcome to PacGame")
character = tk.Label(GameFrame, text = "😐")
IntroLabel = tk.Label(GameFrame,text="Controls:\nwasd: move\nf: equip dynamite/remove dynamite\nmap size selection below. format as \"x,y\"") #WHY THE FUCK DID IT REMOVE THE WHOLE ASS SYSTEM!
ItemLabel = tk.Label(BaseFrame,text="")
MapSizeEntry = tk.Entry(GameFrame)
EnemyCountEntry = tk.Entry(GameFrame)
EnemyCountInfo = tk.Label(GameFrame,text="Enemy count (high numbers cause lag)")
ObjectiveCountEntry = tk.Entry(GameFrame)
ObjectiveCountInfo = tk.Label(GameFrame,text="Objective count")
DynamiteCountEntry = tk.Entry(GameFrame)
DynamiteCountInfo = tk.Label(GameFrame,text="Dynamite count")

StartupGUIs = [
    MapSizeEntry,
    IntroLabel,
    EnemyCountEntry,
    EnemyCountInfo,
    ObjectiveCountEntry,
    ObjectiveCountInfo,
    DynamiteCountEntry,
    DynamiteCountInfo
]

def pygameplaysound(soundname,loopingMusic,volume):
    if platform.system() == "Windows":
        if loopingMusic == True:
            try:
                pygame.mixer.music.load(soundname)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"Could not play sound {soundname}: {e}")

            #winsound.PlaySound(soundname, winsound.SND_ASYNC | winsound.SND_LOOP)
        else:
            snd = pygame.mixer.Sound(soundname)
            snd.set_volume(volume)
            snd.play()

            #winsound.PlaySound(soundname, winsound.SND_ASYNC)

#pregame music
if platform.system() == "Windows":
    threadsoundbgSTARTUP = threading.Thread(target=pygameplaysound,args=('IntermissionNullscape.wav',True,1),daemon=True)
    threadsoundbgSTARTUP.start()

def GenerateMap(SizeX,SizeY,EnemyTotalCount,ObjectiveTotalCount):
    global CurrentMap
    global TopLabel
    global character
    global GridX
    global GridY
    global MoveCD
    global PlayerWin
    global root
    global CloseGame
    global ResetMap
    global KillPlayer
    global DynamiteLeft
    global globaldynamite
    global MapSizeEntry
    global RegenCD
    global StartupGUIs

    ResetMap = True
    KillPlayer = False
    root.config(bg="SystemButtonFace")
    
    try:
        for v in StartupGUIs:
            v.destroy()
    except Exception:
        print('duh')
    else:
        if platform.system() == "Windows":
            #VoidBreakerNullscape.wav
            threadsoundbg = threading.Thread(target=pygameplaysound,args=('VoidscapeVoidExplorerMain.wav',True,0.7),daemon=True)
            threadsoundbg.start()
            

    hasVisited = []

    #visit function for maze algorithm
    def visit(x, y):
        global CurrentMap
        
        NORTH, SOUTH, EAST, WEST = 'n', 's', 'e', 'w'
        unvisitedNeighbors = []
       
        #CurrentMap["Spaces"] maze[(x, y)] = EMPTY
        GridFrame = CurrentMap["Spaces"][str(x) + "," + str(y)]
        GridFrame.config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
       
        unvisitedNeighbors = []
        if y > 1 and (x, y - 2) not in hasVisited: unvisitedNeighbors.append(NORTH)
        if y < CurrentMap["SizeY"] - 2 and (x, y + 2) not in hasVisited: unvisitedNeighbors.append(SOUTH)
        if x > 1 and (x - 2, y) not in hasVisited: unvisitedNeighbors.append(WEST)
        if x < CurrentMap["SizeX"] - 2 and (x + 2, y) not in hasVisited: unvisitedNeighbors.append(EAST)
   
        # Randomly shuffle neighbors to ensure random maze generation
        random.shuffle(unvisitedNeighbors)

        for nextIntersection in unvisitedNeighbors:
            if nextIntersection == NORTH:
                nextX, nextY = x, y - 2
                if (nextX, nextY) not in hasVisited:
                    #maze[(x, y - 1)] = EMPTY # Carve connecting hallway
                    GridFrame = CurrentMap["Spaces"][str(x) + "," + str(y-1)]
                    GridFrame.config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
                    while str(x) + "," + str(y-1) in CurrentMap["Walls"]:
                        CurrentMap["Walls"].remove((str(x) + "," + str(y-1)))
                    hasVisited.append((nextX, nextY))
                    visit(nextX, nextY)
            elif nextIntersection == SOUTH:
                nextX, nextY = x, y + 2
                if (nextX, nextY) not in hasVisited:
                    #maze[(x, y + 1)] = EMPTY
                    GridFrame = CurrentMap["Spaces"][str(x) + "," + str(y+1)]
                    GridFrame.config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
                    while str(x) + "," + str(y+1) in CurrentMap["Walls"]:  
                        CurrentMap["Walls"].remove((str(x) + "," + str(y+1)))
                    hasVisited.append((nextX, nextY))
                    visit(nextX, nextY)
            elif nextIntersection == WEST:
                nextX, nextY = x - 2, y
                if (nextX, nextY) not in hasVisited:
                    #maze[(x - 1, y)] = EMPTY
                    GridFrame = CurrentMap["Spaces"][str(x-1) + "," + str(y)]
                    GridFrame.config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
                    while str(x-1) + "," + str(y) in CurrentMap["Walls"]:
                        CurrentMap["Walls"].remove((str(x-1) + "," + str(y)))
                    hasVisited.append((nextX, nextY))
                    visit(nextX, nextY)
            elif nextIntersection == EAST:
                nextX, nextY = x + 2, y
                if (nextX, nextY) not in hasVisited:
                    #maze[(x + 1, y)] = EMPTY
                    GridFrame = CurrentMap["Spaces"][str(x+1) + "," + str(y)]
                    GridFrame.config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
                    while str(x+1) + "," + str(y) in CurrentMap["Walls"]:
                        CurrentMap["Walls"].remove((str(x+1) + "," + str(y)))
                    hasVisited.append((nextX, nextY))
                    visit(nextX, nextY)

    #reset player pos & stats
    GridX = 0
    GridY = 0
    DynamiteLeft = globaldynamite #3
    CurrentMap["CanWin"] = False
   
    character.grid(column=0,row=0)
   
    CurrentMap["Walls"] = []
   
    if CurrentMap["Spaces"]:
        for i in CurrentMap["Spaces"]:
            v = CurrentMap["Spaces"].get(i)
            #print("destroy",v)
            v.destroy()
    else:
        print("No spaces?")
   
    print("Generating new map...")
    TopLabel.config(text="Generating new map...")
    CurrentMap["SizeX"] = SizeX
    CurrentMap["SizeY"] = SizeY
    print(SizeX,SizeY)
   
    leftY = SizeY
    leftX = SizeX
    currentX = 0
    currentY = 0

    #Create temporary walls
    while leftY >= 0:
        while leftX >= 0:
            leftX -= 1

            rannum = 1 #stupid hacky value
           
            if rannum == 1: #and (currentX > 2 or currentY > 2): #wall
                GridFrame = tk.Frame(GameFrame,bg = "black",bd = 5,relief="raised",height = 25,width = 25)
                GridFrame.grid(column = currentX, row = currentY)
                CurrentMap["Spaces"][str(currentX) + "," + str(currentY)] = GridFrame
                CurrentMap["Walls"].append(str(currentX) + "," + str(currentY))
            else: #refrence for later
                GridFrame = tk.Frame(GameFrame,bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
                GridFrame.grid(column = currentX, row = currentY)
                CurrentMap["Spaces"][str(currentX) + "," + str(currentY)] = GridFrame
           
            currentX += 1
           
        leftY -= 1
        leftX = SizeX
        currentX = 0
        currentY += 1

    #Place goal
    goalX = random.randint(2,SizeX)
    goalY = random.randint(2,SizeY)

    #Draw map
    hasVisited.append((goalX,goalY))
    visit(goalX,goalY)

    #remove spawn walls
    CurrentMap["Spaces"]["0,0"].config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
    if "0,0" in CurrentMap["Walls"]:
        CurrentMap["Walls"].remove("0,0")
    CurrentMap["Spaces"]["1,0"].config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
    if "1,0" in CurrentMap["Walls"]:
        CurrentMap["Walls"].remove("1,0")
    CurrentMap["Spaces"]["0,1"].config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
    if "0,1" in CurrentMap["Walls"]:
        CurrentMap["Walls"].remove("0,1")
    CurrentMap["Spaces"]["1,1"].config(bg = "lightblue",bd = 1,relief="solid",height = 25,width = 25)
    if "1,1" in CurrentMap["Walls"]:
        CurrentMap["Walls"].remove("1,1")
    
    leftY = SizeY
    leftX = SizeX
    currentX = 0
    currentY = 0

    #Remove stupid idiot walls (and enemies)
    CurrentMap["Enemies"].clear()
    CurrentMap["Objectives"].clear()
    
    while leftY >= 0:
        while leftX >= 0:
            leftX -= 1
           
            GridFrame = CurrentMap["Spaces"][str(currentX) + "," + str(currentY)]
           
            if GridFrame.cget("relief") == "solid" and str(currentX) + "," + str(currentY) in CurrentMap["Walls"]:
                CurrentMap["Walls"].remove(str(currentX) + "," + str(currentY))
           
            currentX += 1
           
        leftY -= 1
        leftX = SizeX
        currentX = 0
        currentY += 1

    def DelayResetMap():
        global ResetMap
        
        time.sleep(1)
        ResetMap = False

    thread0 = threading.Thread(target=DelayResetMap,args=(),daemon=True)
    thread0.start()
       
    #SpawnGoal
    if CurrentMap["Spaces"][str(goalX) + "," + str(goalY)]:
        GoalSpace = CurrentMap["Spaces"][str(goalX) + "," + str(goalY)]
        GoalSpace.config(bg = "green")
       
        CurrentMap["GoalSpace"] = str(goalX) + "," + str(goalY)
        CurrentMap["TKGoalSpace"] = GoalSpace
       
        #if GoalSpace.cget("relief") == "raised":
        #    GoalSpace.config(relief = "solid",bd = 1)
        #    CurrentMap["Walls"].remove(str(goalX) + "," + str(goalY))
    else:
        print("NO SPACE???")

    #Create enemies
    evilGuysToSpawn = random.randint(1,4)
    if EnemyTotalCount != "" and EnemyTotalCount != None:
        evilGuysToSpawn = EnemyTotalCount
    EvilGuys = 0
    
    def EnemyCollisionCheck(Enem,EnemDict):
        global CurrentMap
        global ResetMap
        global PlayerWin
        global CloseGame
        global GridX
        global GridY
        global KillPlayer
        
        while PlayerWin == False and CloseGame == False and ResetMap == False:
            if EnemDict["Position"] in CurrentMap["Spaces"]:
                if EnemDict["PosIntXY"] == (GridX,GridY):
                    #print("KILL DEAD DIE")
                    KillPlayer = True
                    
            time.sleep(0.1)
    
    def EnemyFunction(gooberNum):
        global CurrentMap
        global PlayerWin
        global root
        global ResetMap
        global KillPlayer
        
        #print("wow im so evil")
        
        #Create enemy
        Enemy = tk.Label(GameFrame, text = "😡", bg = "red")

        #initiate dict
        CurrentMap["Enemies"]["Enemy" + str(gooberNum)] = {
            "Exists": True,
            "Position": "0,0",
            "PosIntYX": (0,0),
            "PosIntXY": (0,0),
            "EnemyType": "Normal",
            "Thread": None
        }
        EnemyDictEntry = CurrentMap["Enemies"]["Enemy" + str(gooberNum)]
        
        yaryayr = random.randint(1,3)
        if yaryayr == 1:
            #When on pc it looks HUGE so im removing it temporarily
            EnemyDictEntry["EnemyType"] = "Train"
            image_file = tk.PhotoImage(file="trainImage.gif")
            image_file = image_file.subsample(12, 10)
            if platform.system() == "Windows":
                Enemy.config(text="🚂",font=("Arial",8))
            else:
                Enemy.config(text="🚂",font=("Arial",8),image = image_file)
            
            #print("choochoo")
            
            #Enemy.image = image_file
        
        RetrySpawn = True
        
        while RetrySpawn == True:
            SpawnX,SpawnY = random.randint(5,CurrentMap["SizeX"]), random.randint(5,CurrentMap["SizeY"])
            SpawnPosStr = str(SpawnX) + "," + str(SpawnY)
        
            #spawn checks
            EntityOccupyingSpace = False
            for i,v in CurrentMap["Enemies"].items():
                if v and v["Position"] == SpawnPosStr:
                    EntityOccupyingSpace = True
        
            if not SpawnPosStr in CurrentMap["Walls"] and EntityOccupyingSpace == False:
                Enemy.grid(row=SpawnY,column=SpawnX)
                Enemy.lift()
                EnemyDictEntry["Position"] = SpawnPosStr
                EnemyDictEntry["PosIntYX"] = (SpawnY,SpawnX)
                EnemyDictEntry["PosIntXY"] = (SpawnX,SpawnY)
                RetrySpawn = False
        
        def TextifyMap():
            global CurrentMap
            
            Map = []
            # Wall = "#"
            # Empty = " "
            
            leftY = CurrentMap["SizeY"]
            leftX = CurrentMap["SizeX"]
            currentX = 0
            currentY = 0
            
            while leftY >= 0:
                Row = []
                while leftX >= 0:
                    leftX -= 1
                    
                    GridFrame = CurrentMap["Spaces"][str(currentX) + "," + str(currentY)]
                    
                    if str(currentX) + "," + str(currentY) in CurrentMap["Walls"] or GridFrame.cget("relief") == "raised":
                        Row.append("#")
                        #print("Wall",currentX,currentY)
                    else:
                        Row.append(" ")
                
                    currentX += 1
                
                leftY -= 1
                leftX = SizeX
                currentX = 0
                currentY += 1
                Map.append(Row)
                #Map.insert(0,Row) #insert at back
            
            #print(Map)
            return Map
        
        #PATHFIND ALGORYTHM
        def solve_maze_bfs(maze, start, end):
            global GridX
            global GridY
            
            """
            Solves a maze using Breadth-First Search.
    
            Args:
                maze: A 2D list representing the maze.
                start: A tuple (row, col) for the start position.
                end: A tuple (row, col) for the end position.
    
            Returns:
             A list of coordinates representing the shortest path, or None if no path exists.
            """
            # Queue stores tuples of (current_position, path_taken)
            queue = collections.deque([(start, [start])])
            visited = set([start])
    
            # Possible movements: up, down, left, right
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            while queue:
                (curr_r, curr_c), path = queue.popleft() # Dequeue the front element

                # Check if the current cell is the end
                if (curr_r, curr_c) == end:
                    #print(curr_r,curr_c)
                    return path

            # Explore neighbors
                for dr, dc in directions:
                    next_r, next_c = curr_r + dr, curr_c + dc

                    # Check if the move is valid (within bounds, not a wall, and not visited)
                    if 0 <= next_r < len(maze) and 0 <= next_c < len(maze[0]):
                        if maze[next_r][next_c] != '#' and (next_r, next_c) not in visited:
                            visited.add((next_r, next_c))
                            # Enqueue the neighbor and the updated path
                            new_path = list(path) + [(next_r, next_c)]
                            queue.append(((next_r, next_c), new_path))
    
            return None # No path found

        while ResetMap == True:
            time.sleep(0.1)
            
        thread = threading.Thread(target=EnemyCollisionCheck,args=(Enemy,EnemyDictEntry,),daemon=True)
        thread.start()
        
        while EnemyDictEntry and EnemyDictEntry["Exists"] == True and CloseGame == False and ResetMap == False:
            #print("MakeListMap")
            ListMap = TextifyMap()
            start_pos = EnemyDictEntry["PosIntYX"]
            end_pos = (GridY, GridX)
            shortest_path = solve_maze_bfs(ListMap, start_pos, end_pos)
            
            MovesBeforeRecalc = 4
            
            if shortest_path:
                #print("Shortest path found:", shortest_path)

                if EnemyDictEntry["EnemyType"] == "Train":
                    threadsoundtrain = threading.Thread(target=pygameplaysound,args=("trainHorn.mp3",False,0.5),daemon=True)
                    threadsoundtrain.start()
                
                for y,x in shortest_path: #use y,x
                    EnemyDictEntry["Position"] = SpawnPosStr
                    EnemyDictEntry["PosIntYX"] = (y,x)
                    EnemyDictEntry["PosIntXY"] = (x,y)
                    Enemy.grid(row=y,column=x)
                    Enemy.lift()
                    
                    MovesBeforeRecalc -= 1
                    
                    if PlayerWin == True or CloseGame == True or ResetMap == True:
                        print("waah I suck -Enemy" + str(gooberNum))
                        Enemy.config(text="😭")
                        EnemyDictEntry["Exists"] == False
                        
                        if ResetMap == True:
                            Enemy.destroy()
                            return
                        
                        while PlayerWin == True or CloseGame == True:
                            time.sleep(0.1)
                        
                        Enemy.destroy()
                        return
                    elif KillPlayer == True:
                        print("RAAH I WIN 💀🛡💥 -Enemy" + str(gooberNum))
                        Enemy.config(text="😎")
                        EnemyDictEntry["Exists"] == False
                        
                        if ResetMap == True:
                            Enemy.destroy()
                            return
                        
                        while KillPlayer == True or CloseGame == True:
                            time.sleep(0.1)
                        
                        Enemy.destroy()
                        return
                    
                    if MovesBeforeRecalc <= 0 and EnemyDictEntry["EnemyType"] != "Train":
                        break
                    
                    if EnemyDictEntry["EnemyType"] == "Train":
                        time.sleep(0.1)
                    else:
                        time.sleep(0.5)
            else:
                print("No path exists.")
            
            if EnemyDictEntry["EnemyType"] == "Train":
                time.sleep(2)
            
        print("Enemy died?")
        return
    
    def EnemyThreadAdder(thred,enemyint):
        global CurrentMap
        
        while not "Enemy" + str(enemyint) in CurrentMap["Enemies"]:
            time.sleep(0.1)
        
        print("Thread added for " + "Enemy" + str(enemyint))
        CurrentMap["Enemies"]["Enemy" + str(enemyint)]["Thread"] = thred
        return
    
    while evilGuysToSpawn > 0:
        EvilGuys += 1
        thread = threading.Thread(target=EnemyFunction,args=(EvilGuys,),daemon=True)
        thread.start()
        
        thread2 = threading.Thread(target=EnemyThreadAdder, args=(thread,EvilGuys,))
        thread2.start()
        #asyncio.run(EnemyFunction(EvilGuys))
        evilGuysToSpawn -= 1
        #print("evil")
        
    #Spawn objectives
    def ObjectiveFunction(ObjNum):
        global CurrentMap
        global PlayerWin
        global root
        global ResetMap
        global KillPlayer
        
        #print("wow im so cool and awesome")
        
        #Create objective
        Objective = tk.Label(GameFrame, text = "☆", bg = "gold", font = ("Noto Sans Symbols",11))
        
        #initiate dict
        CurrentMap["Objectives"]["Objective" + str(ObjNum)] = {
            "Exists": True,
            "Collected": False,
            "TKObject": Objective,
            "Position": "0,0",
            "PosIntYX": (0,0),
            "PosIntXY": (0,0),
            "ObjectiveType": "Normal",
            "Thread": None
        }
        ObjDictEntry = CurrentMap["Objectives"]["Objective" + str(ObjNum)]
        
        RetrySpawn = True
        
        while RetrySpawn == True:
            SpawnX,SpawnY = random.randint(5,CurrentMap["SizeX"]), random.randint(5,CurrentMap["SizeY"])
            SpawnPosStr = str(SpawnX) + "," + str(SpawnY)
        
            #spawn checks
            EntityOccupyingSpace = False
            for i,v in CurrentMap["Enemies"].items():
                if v and v["Position"] == SpawnPosStr:
                    EntityOccupyingSpace = True
        
            if not SpawnPosStr in CurrentMap["Walls"] and EntityOccupyingSpace == False:
                Objective.grid(row=SpawnY,column=SpawnX)
                Objective.lift()
                ObjDictEntry["Position"] = SpawnPosStr
                ObjDictEntry["PosIntYX"] = (SpawnY,SpawnX)
                ObjDictEntry["PosIntXY"] = (SpawnX,SpawnY)
                RetrySpawn = False
    
    ObjectivesLeft = 3
    if ObjectiveTotalCount != "" and ObjectiveTotalCount != None:
        ObjectivesLeft = ObjectiveTotalCount
    Objectives = 0
    
    while ObjectivesLeft > 0:
        Objectives += 1
        
        thread0 = threading.Thread(target=ObjectiveFunction,args=(Objectives,),daemon=True)
        thread0.start()
        
        ObjectivesLeft -= 1
        #print("awesome")
    
    def goalManager():
        global CurrentMap
        global GameFrame
        
        LockLabel = None
        
        time.sleep(0.2)
        
        if len(CurrentMap["Objectives"]) > 1:
            print(CurrentMap["TKGoalSpace"])
            LockLabel = tk.Label(GameFrame,text="X",bg="red")
            posx,posy = CurrentMap["GoalSpace"].split(",")
            LockLabel.grid(column=int(posx), row=int(posy))
            LockLabel.lift()
            
            CompletedObjectives = False
            
            while CompletedObjectives == False:
                time.sleep(0.1)
                Complete = 0
                CurrentMap["CanWin"] = False
                
                for i,v in CurrentMap["Objectives"].items():
                    if v["Collected"] == True:
                        Complete += 1
                
                if Complete >= len(CurrentMap["Objectives"]):
                    CompletedObjectives = True
                    LockLabel.destroy()
                    CurrentMap["CanWin"] = True
                    root.config(bg="gold")
                    if platform.system() == "Windows":
                        escapemsgs = [
                            "Get out!",
                            "Escape!",
                            "Run!",
                            "The lock broke!"
                        ]

                        TopLabel.config(text=random.choice(escapemsgs))
                        if len(CurrentMap["Enemies"]) < 10:
                            threadsoundbg = threading.Thread(target=pygameplaysound,args=("VoidscapeVoidExplorerGOLD.wav",True,0.7),daemon=True)
                            threadsoundbg.start()
                        
        else:
            print("No objectives?")
            print(CurrentMap["Objectives"])
            CurrentMap["CanWin"] = True
   
    #TKGoalSpace
    goalOpenerThread = threading.Thread(target=goalManager,daemon=True)
    goalOpenerThread.start()
    
    #initiate game
    MoveCD = False
    PlayerWin = False
    TopLabel.config(text="PacGame " + Version)
    character.config(text="😐")
    character.lift()
    TopLabel.grid(column=2, row=0)
    button.grid(column=0, row=0)
    MapGenButton.grid(column=1, row=0)
    print("end")

    def tempfunc():
        time.sleep(0.2)
        if len(CurrentMap["Enemies"]) >= 10:
            threadsoundbg2 = threading.Thread(target=pygameplaysound,args=('VoidBreakerNullscape.wav',True,0.7),daemon=True)
            threadsoundbg2.start()
    
    if platform.system() == "Windows": #special evil music
        stinkystupidthread = threading.Thread(target=tempfunc,daemon=True)
        stinkystupidthread.start()

def key_press(event):
    """Callback function to handle a key press event."""
    # event.char contains the character of the key pressed (if applicable)
    # event.keysym contains the symbolic name of the key (e.g., 'Return', 'Caps_Lock', 'a')
    # event.keycode contains the system-specific key code
   
    global CurrentMap
    global GridY
    global GridX
    global MoveCD
    global TopLabel
    global PlayerWin
    global KillPlayer
    global ItemLabel
    global DynamiteToggled
    global DynamiteLeft
    global root

    key = event.char
    if key and MoveCD == False and KillPlayer == False:
        if event.keysym == "w":
            #print("fwd")
            if (GridY - 1) >= 0 and (GridY - 1) <= CurrentMap["SizeY"] and not str(GridX) + "," + str((GridY - 1)) in CurrentMap["Walls"]:
                GridY -= 1
                character.grid(column=GridX, row=GridY)
                character.lift()
                
                for i,v in CurrentMap["Objectives"].items():
                    if v["PosIntXY"] == (GridX,GridY) and v["Collected"] == False:
                        print("collect objective "+i)
                        if platform.system() == "Windows":
                            winsound.PlaySound('Collect.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                        v["Collected"] = True
                        v["TKObject"].destroy()
               
                print(GridX,GridY)
            else:
                print("Cant move there!")
                if DynamiteToggled == True:
                    BreakPos = str(GridX) + "," + str((GridY - 1))
                    
                    if BreakPos in CurrentMap["Walls"] and DynamiteLeft > 0:
                        DynamiteLeft -= 1
                        ItemLabel.config(text="🧨 "+ str(DynamiteLeft) +" charges")

                        if platform.system() == "Windows":
                            winsound.PlaySound('rbxExplosion.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

                        CurrentMap["Walls"].remove(BreakPos)
                        CurrentMap["Spaces"][BreakPos].config(bg = "lightblue4",bd = 2,relief="sunken",height = 25,width = 25)
        elif event.keysym == "a":
            #print("left")
            if (GridX - 1) >= 0 and (GridX - 1) <= CurrentMap["SizeX"] and not str((GridX - 1)) + "," + str(GridY) in CurrentMap["Walls"]:
                GridX -= 1
                character.grid(column=GridX, row=GridY)
                character.lift()
                
                for i,v in CurrentMap["Objectives"].items():
                    if v["PosIntXY"] == (GridX,GridY) and v["Collected"] == False:
                        print("collect objective "+i)
                        if platform.system() == "Windows":
                            winsound.PlaySound('Collect.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                        v["Collected"] = True
                        v["TKObject"].destroy()
                
                print(GridX,GridY)
            else:
                print("Cant move there!")
                if DynamiteToggled == True:
                    BreakPos = str(GridX - 1) + "," + str((GridY))
                    
                    if BreakPos in CurrentMap["Walls"] and DynamiteLeft > 0:
                        DynamiteLeft -= 1
                        ItemLabel.config(text="🧨 "+ str(DynamiteLeft) +" charges")

                        if platform.system() == "Windows":
                            winsound.PlaySound('rbxExplosion.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

                        CurrentMap["Walls"].remove(BreakPos)
                        CurrentMap["Spaces"][BreakPos].config(bg = "lightblue4",bd = 2,relief="sunken",height = 25,width = 25)
        elif event.keysym == "s":
            #print("dwn")
            if (GridY + 1) >= 0 and (GridY + 1) <= CurrentMap["SizeY"] and not str(GridX) + "," + str((GridY + 1)) in CurrentMap["Walls"]:
                GridY += 1
                character.grid(column=GridX, row=GridY)
                character.lift()
                
                for i,v in CurrentMap["Objectives"].items():
                    if v["PosIntXY"] == (GridX,GridY) and v["Collected"] == False:
                        print("collect objective "+i)
                        if platform.system() == "Windows":
                            winsound.PlaySound('Collect.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                        v["Collected"] = True
                        v["TKObject"].destroy()
               
                print(GridX,GridY)
            else:
                print("Cant move there!")
                if DynamiteToggled == True:
                    BreakPos = str(GridX) + "," + str((GridY + 1))
                    
                    if BreakPos in CurrentMap["Walls"] and DynamiteLeft > 0:
                        DynamiteLeft -= 1
                        ItemLabel.config(text="🧨 "+ str(DynamiteLeft) +" charges")

                        if platform.system() == "Windows":
                            winsound.PlaySound('rbxExplosion.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                        
                        CurrentMap["Walls"].remove(BreakPos)
                        CurrentMap["Spaces"][BreakPos].config(bg = "lightblue4",bd = 2,relief="sunken",height = 25,width = 25)
                #if str(GridX) + "," + str((GridY + 1)) in CurrentMap["Walls"]:
                #    print("I HATE YOU!!!")
        elif event.keysym == "d":
            #print("right")
            if (GridX + 1) >= 0 and (GridX + 1) <= CurrentMap["SizeX"] and not str((GridX + 1)) + "," + str(GridY) in CurrentMap["Walls"]:
                GridX += 1
                character.grid(column=GridX, row=GridY)
                character.lift()
                
                for i,v in CurrentMap["Objectives"].items():
                    if v["PosIntXY"] == (GridX,GridY) and v["Collected"] == False:
                        print("collect objective "+i)
                        if platform.system() == "Windows":
                            winsound.PlaySound('Collect.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                        v["Collected"] = True
                        v["TKObject"].destroy()
               
                print(GridX,GridY)
            else:
                print("Cant move there!")
                if DynamiteToggled == True:
                    BreakPos = str(GridX + 1) + "," + str((GridY))
                    
                    if BreakPos in CurrentMap["Walls"] and DynamiteLeft > 0:
                        DynamiteLeft -= 1
                        ItemLabel.config(text="🧨 "+ str(DynamiteLeft) +" charges")
                        
                        if platform.system() == "Windows":
                            winsound.PlaySound('rbxExplosion.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                        
                        CurrentMap["Walls"].remove(BreakPos)
                        CurrentMap["Spaces"][BreakPos].config(bg = "lightblue4",bd = 2,relief="sunken",height = 25,width = 25)
        elif event.keysym == "f":
            print("Im dynaing the myte")
            
            if DynamiteToggled == False:
                DynamiteToggled = True
                ItemLabel.config(text="🧨 "+ str(DynamiteLeft) +" charges")
            else:
                DynamiteToggled = False
                ItemLabel.config(text="")
            
       # print(f"'{key}' pressed. Keysym: {event.keysym}, Keycode: {event.keycode}")
       
        if str(GridX) + "," + str(GridY) == CurrentMap["GoalSpace"] and CurrentMap["CanWin"] == True:
            print("winner winner chicken dinner")
            character.config(text="😀")

            winmsgs = [
                "You win!",
                "Nice one!",
                "Your on a roll!",
                "Broken free!",
                "🦅"
            ]

            TopLabel.config(text=random.choice(winmsgs))
            if platform.system() == "Windows":
                 winsound.PlaySound('Victory.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

            MoveCD = True
            PlayerWin = True
    else:
        if KillPlayer == True:
            if platform.system() == "Windows" and TopLabel.cget("text") != "Better luck next time!":
                pygame.mixer.music.stop()
                winsound.PlaySound('ouchdeath.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
                root.config(bg="darkred")
            else:
                root.bell()
            
            character.config(text="😭")
            TopLabel.config(text="Better luck next time!")
        
        print("cant move right now or invalid key")

mapsizeconst = "15,13"
enemyamountconst = None
objectiveamountconst = None

def MapGenerationInitiation():
    global root
    global mapsizeconst
    global enemyamountconst
    global objectiveamountconst
    global RegenCD
    global globaldynamite
    #global EnemyCountEntry
    #global ObjectiveCountEntry
    
    if RegenCD == False:
        #RegenCD = True
        
        try:
            playerinput = MapSizeEntry.get()
        except Exception:
            playerinput = mapsizeconst

        try:
            DynamiteCountEntry.get()
        except Exception:
            print("default dynamite")
        else:
            if DynamiteCountEntry.get().isnumeric() == True:
                globaldynamite = int(DynamiteCountEntry.get())
        
        #try except block hellscape
        #not sure why its goign through with the geostring and still doing other stuff...
        try:
            MapSizX,MapSizY = playerinput.split(",")
            MapSizeX,MapSizeY = int(MapSizX),int(MapSizY)
            #int(EnemyCountEntry.get())
            #int(ObjectiveCountEntry.get())
        except Exception as e0:
            print(e0)
            try:
                enemyamountconst = int(EnemyCountEntry.get())
                objectiveamountconst = int(ObjectiveCountEntry.get())
            except Exception as e:
                try:
                    int(EnemyCountEntry.get())
                except Exception:
                    try:
                        objectiveamountconst = int(ObjectiveCountEntry.get())
                    except Exception:
                        print("amogus")
                        GenerateMap(15,13,enemyamountconst,objectiveamountconst)
                    else:
                        print(objectiveamountconst)
                        GenerateMap(15,13,enemyamountconst,int(ObjectiveCountEntry.get()))
                else:
                    enemyamountconst = int(EnemyCountEntry.get())
                    
                    GenerateMap(15,13,int(EnemyCountEntry.get()),objectiveamountconst)
            else:
                GenerateMap(15,13,int(EnemyCountEntry.get()),int(ObjectiveCountEntry.get()))
        else: #if that works
            mapsizeconst = playerinput
            MapSizX,MapSizY = playerinput.split(",")
            MapSizeX,MapSizeY = int(MapSizX),int(MapSizY)
            
            enemyamountstr = None
            
            try:
                EnemyCountEntry.get()
            except Exception:
                enemyamountstr = str(enemyamountconst)
            else:
                enemyamountstr = EnemyCountEntry.get()
                enemyamountconst = enemyamountstr
            
            if enemyamountstr == "" or enemyamountstr == None:
                enemyamountstr = ""
            
            objectiveamountstr = None
            
            try:
                ObjectiveCountEntry.get()
            except Exception:
                objectiveamountstr = str(objectiveamountconst)
            else:
                objectiveamountstr = ObjectiveCountEntry.get()
                objectiveamountconst = objectiveamountstr
            
            if objectiveamountstr == "" or objectiveamountstr == None:
                objectiveamountstr = ""
                
            enemyamount = None
            objectiveamount = None
            
            if enemyamountstr.isdigit() == True: #just realised ,isdigit() exists and I feel really stupid
                enemyamount = int(enemyamountstr)
            else:
                enemyamount = None
            
            if objectiveamountstr.isdigit() == True:
                objectiveamount = int(objectiveamountstr)
            else:
                objectiveamount = None
            
            geostring = str(MapSizeX*26) + "x" + str(MapSizeY*28)
            #if MapSizeX < 15:
            #    geostring = str(15*26) + "x" + str(MapSizeY*31)
            root.geometry(geostring)
            print(geostring,MapSizeX,MapSizeY)
            GenerateMap(MapSizeX,MapSizeY,enemyamount,objectiveamount)
    else:
        print("Map regen is on cooldown!")

MapGenButton = tk.Button(BaseFrame, text = "GenMap", command = lambda: MapGenerationInitiation())

#grid and display init
root.bind('<Key>', key_press)
GameFrame.grid(column=0,row=1)
character.grid(column=0, row=0)
TopLabel.grid(column=3, row=0)
button.grid(column=0, row=0)
MapGenButton.grid(column=1, row=0)
IntroLabel.grid(column=0, row=1)
ItemLabel.grid(column=4, row=0)
MapSizeEntry.grid(column=0, row=2)
EnemyCountEntry.grid(column=0, row=4)
EnemyCountInfo.grid(column=0, row=3)
ObjectiveCountEntry.grid(column=0, row=6)
ObjectiveCountInfo.grid(column=0, row=5)
DynamiteCountInfo.grid(column=0, row=7)
DynamiteCountEntry.grid(column=0, row=8)

root.mainloop()
