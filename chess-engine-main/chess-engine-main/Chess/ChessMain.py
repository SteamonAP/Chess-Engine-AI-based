import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
import win32api
import pygame as p
from Chess import ChessEngine
from Chess import SmartMoveFinder
from multiprocessing import Process, Queue

import cv2
import mediapipe as mp
import pyautogui

# Constants
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages(): 
    """Initialize a global dictionary of images. This will be called once in the main."""
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"chess-engine-main\Chess\images\{piece}.png"), (SQ_SIZE, SQ_SIZE))
        
        


def main():
    threading.Thread(target=handRecognition, daemon=True).start()

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Arial", 16, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # Flag for when a move is made
    animate = False
    loadImages()
    running = True
    sqSelected = ()  # No square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = []  # Keep track of player clicks (two tuples: [(6, 4), (4, 4)] for e2e4)
    gameOver = False
    playerOne = True  # If a human is playing white, this will be True. If an AI is playing white, then False.
    playerTwo = False  # If a human is playing black, this will be True. If an AI is playing black, then False.
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while running:
        humanTurn = (gs.whitetoMove and playerOne) or (not gs.whitetoMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:  # The user clicked the same square twice
                        sqSelected = ()  # Deselect
                        playerClicks = []  # Clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # Append for both 1st and 2nd clicks
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # Reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True                        

                if e.key == p.K_r:  # Reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False                    
                    moveUndone = True

        # AI move finder logic
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("Let me cook....")
                returnQueue = Queue()
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()
            if not moveFinderProcess.is_alive():
                print("done cooking")
                AIMove = returnQueue.get()                
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            
            drawEndGameText(screen,'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whitetoMove else 'White wins by checkmate');    
   

        clock.tick(MAX_FPS)
        p.display.flip()

    p.quit()


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    """Draw the current game state on the screen."""
    drawBoard(screen)  # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # Draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)
    
def drawBoard(screen):
    """Draw the squares on the board. The top left square is always light."""
    global colors
    colors = [p.Color("white"), p.Color("brown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))    

def highlightSquares(screen, gs, validMoves, sqSelected):
    """Highlight square selected and moves for piece selected."""
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whitetoMove else 'b'):  # Check if it's the correct player's turn
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('green'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # Highlight possible moves
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawPieces(screen, board):
    """Draw the pieces on the board using the current GameState.board."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not an empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
def drawMoveLog(screen, gs, font):
    
    """Draw the end game text on the screen."""
    
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)
    movesPerRow = 3                             
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing
          

def animateMove(move, screen, board, clock):
    """Animate a move."""
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r = move.startRow + dR * frame / frameCount
        c = move.startCol + dC * frame / frameCount
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece onto the rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)            
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    """Draw the end game text on the screen."""
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

def resetGame():
    """Reset the game board."""
    moveFinderProcess = None
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    sqSelected = ()
    playerClicks = []
    moveMade = False
    animate = False
    gameOver = False
    if AIThinking:
        moveFinderProcess.terminate()
        AIThinking = False                    
    moveUndone = True

# Now from here is the Hand recognition code
def handRecognition():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    hand_detector = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    drawing_utils = mp.solutions.drawing_utils
    screen_width, screen_height = pyautogui.size()
    index_y = 0
    peace_sign_detected = False
    last_reset_time = 0  # Initialize the last reset time
    reset_cooldown = 10   # Cooldown in seconds
    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = hand_detector.process(rgb_frame)
        hands = output.multi_hand_landmarks
        if hands:
            for hand in hands:
                drawing_utils.draw_landmarks(frame, hand)
                landmarks = hand.landmark
                fingers_extended = []

                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x*frame_width)
                    y = int(landmark.y*frame_height)

                    if id == 4: # thumb
                        cv2.circle(img=frame, center=(x,y), radius=10, color=(0,255,255))
                        thumb_x = screen_width/frame_width*x
                        thumb_y = screen_height/frame_height*y
                        pyautogui.moveTo(thumb_x,thumb_y)

                    if id == 8: # index finger
                        cv2.circle(img=frame, center=(x,y), radius=10, color=(0,255,255))
                        index_x = screen_width/frame_width*x
                        index_y = screen_height/frame_height*y
                        print('outside', abs(thumb_y - index_y))
                        if abs(thumb_y - index_y) < 45:
                            pyautogui.click()
                            time.sleep(1)
                            print('click')
                    
                    # Detect index finger up
                    if landmarks[8].y < landmarks[6].y:
                        fingers_extended.append(True)
                    else:
                        fingers_extended.append(False)

                    # Detect middle finger up
                    if landmarks[12].y < landmarks[10].y:
                        fingers_extended.append(True)
                    else:
                        fingers_extended.append(False)

                    # Detect ring and pinky fingers down
                    if landmarks[16].y > landmarks[14].y and landmarks[20].y > landmarks[18].y:
                        fingers_extended.extend([False, False])
                    else:
                        fingers_extended.extend([True, True])  # Set to true if either ring or pinky is up

                    # Check if only the peace sign (index and middle fingers) is up
                    if fingers_extended == [True, True, False, False]:
                        current_time = time.time()
                        if not peace_sign_detected and (current_time - last_reset_time > reset_cooldown):
                            print("Peace sign detected - resetting board")
                            # Trigger reset by sending an event
                            p.event.post(p.event.Event(p.KEYDOWN, key=p.K_r))
                            last_reset_time = current_time  # Update the last reset time
                            peace_sign_detected = True
                    else:
                        peace_sign_detected = False  # Reset flag when peace sign is no longer detected


        cv2.imshow("Hand Cam", frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()

