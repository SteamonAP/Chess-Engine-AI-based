class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        
        self.moveFunctions = {'p':self.getPawnMoves, 'R':self.getRookMoves, 'N':self.getKnightMoves,
                              'B':self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whitetoMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)]


    
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whitetoMove = not self.whitetoMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
            
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
            
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
            
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
            
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'   
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'                            
        self.enpassantPossibleLog.append(self.enpassantPossible)            


        
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs,self.currentCastlingRights.bqs))
        
                  

                               

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whitetoMove = not self.whitetoMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
                
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]                
                
                

                
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]
            # self.currentCastlingRights = CastleRights(newRights.wks,newRights.bks,newRights.wps,newRights.bqs)
            
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
                    
            self.checkmate = False
            self.stalemate = False                                       
                    
                          
            
    def updateCastleRights(self, move):
    # If the king moves, lose both kingside and queenside castling rights for that color
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        # If a rook moves, lose the specific castling right
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # Left rook (queenside)
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # Right rook (kingside)
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # Left rook (queenside)
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # Right rook (kingside)
                    self.currentCastlingRights.bks = False

        # If a rook is captured, lose the specific castling right
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:  # Left rook (queenside)
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:  # Right rook (kingside)
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:  # Left rook (queenside)
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:  # Right rook (kingside)
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
                    
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)
        moves = self.getAllPossibleMoves()
        if self.whitetoMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
                
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whitetoMove = not self.whitetoMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whitetoMove = not self.whitetoMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights                                    
        return moves

    def inCheck(self):
        if self.whitetoMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
        
        
        
    def squareUnderAttack(self, r, c):
        self.whitetoMove = not self.whitetoMove
        oppMoves = self.getAllPossibleMoves()
        self.whitetoMove = not self.whitetoMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    
    
                
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whitetoMove) or (turn == "b" and not self.whitetoMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whitetoMove:  # White pawn moves
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
                            
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))    
        else:  # Black pawn moves
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))                    
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))                    

    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        enemyColor = "b" if self.whitetoMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        allyColor = "w" if self.whitetoMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  
        enemyColor = "b" if self.whitetoMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)  
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        allyColor = "w" if self.whitetoMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

        
        
    def getCastleMoves(self, r, c, moves):
        
        if self.squareUnderAttack(r, c):
            return
       
        if (self.whitetoMove and self.currentCastlingRights.wks) or (not self.whitetoMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        
        if (self.whitetoMove and self.currentCastlingRights.wqs) or (not self.whitetoMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

            
            
                                                        


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        
        self.isCapture = self.pieceCaptured != '--'
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"
        
        endSquare = self.getRankFile(self.endRow, self.endCol)
        
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare              
            else:
                return endSquare           
        
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare

                          
        
        
            