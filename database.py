from datetime import datetime
import sys

from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import sqlite3
from PyQt5 import QtWidgets, QtCore

# Create the connection
con = QSqlDatabase.addDatabase("QSQLITE") #type of db
con.setDatabaseName("SeniorNotes.sqlite")

# Open the connection
if not con.open():
    print("Database Error: %s" % con.lastError().databaseText())
    sys.exit(1)

# Create a query and execute it right away using .exec()
createTableQuery = QSqlQuery()
createTableQuery.exec(
    """
    CREATE TABLE IF NOT EXISTS StudentTable  (
        studentName VARCHAR(40) NOT NULL,
        email VARCHAR(40) NOT NULL,
        studentId INT NOT NULL, 
        groupId VARCHAR(40) NOT NULL, 
        CONSTRAINT FK_GroupId
        FOREIGN KEY (groupId) REFERENCES GroupTable(groupId)
    )
    """
)
createTableQuery.exec(
    """
    CREATE TABLE IF NOT EXISTS GroupTable  (
        groupNum INT NOT NULL,
        groupName VARCHAR(40) NOT NULL,
        meetingday VARCHAR(10) NOT NULL,
        meetingtime DATETIME NOT NULL,
        whichClass VARCHAR(40) NOT NULL, 
        section INT NOT NULL, 
        semester VARCHAR(40) NOT NULL,
        groupId VARCHAR(40) PRIMARY KEY NOT NULL

    )
    """
)
createTableQuery.exec(
    """
    CREATE TABLE IF NOT EXISTS GroupNotes(
        date VARCHAR(25) PRIMARY KEY NOT NULL,
        notes VARCHAR(10000) NOT NULL,
        groupId VARCHAR(40) NOT NULL,
        CONSTRAINT FK_GID
        FOREIGN KEY (groupId) REFERENCES GroupTable(groupId)
    )
    """
)


print(con.tables())


def insertintoGroup(gname, gnum, mday, mtime, cnum, csec, csem, gid):

    insertIntoGroupQuery = QSqlQuery()
    insertIntoGroupQuery.prepare(
        """
            INSERT INTO GroupTable (groupName, groupNum, meetingday, meetingtime, whichClass, section, semester, groupId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            
        """
    )
    groupData = [(gname, gnum, mday, mtime, cnum, csec, csem, gid)]
    for gname, gnum, mday, mtime, cnum, csec, csem, gid in groupData:
        insertIntoGroupQuery.addBindValue(gname)
        insertIntoGroupQuery.addBindValue(gnum)
        insertIntoGroupQuery.addBindValue(mday)
        insertIntoGroupQuery.addBindValue(mtime)
        insertIntoGroupQuery.addBindValue(cnum)
        insertIntoGroupQuery.addBindValue(csec)
        insertIntoGroupQuery.addBindValue(csem)
        insertIntoGroupQuery.addBindValue(gid)
        insertIntoGroupQuery.exec()



def insertintoNotes(date, notes, gid):
    insertIntoNotesQuery = QSqlQuery()
    insertIntoNotesQuery.prepare(
        """
            INSERT INTO GroupNotes (date, notes, groupId)
            VALUES (?, ?, ?)
            
        """
    )
    groupNoteData = [(date, notes, gid)]
    for date, notes, gid in groupNoteData:
        insertIntoNotesQuery.addBindValue(date)
        insertIntoNotesQuery.addBindValue(notes)
        insertIntoNotesQuery.addBindValue(gid)
        insertIntoNotesQuery.exec()

def insertintoStudent(sname, email, sid, gid):

    insertIntoStudentQuery = QSqlQuery()
    insertIntoStudentQuery.prepare(
        """
            INSERT INTO StudentTable (studentName, email, studentId, groupId)
            VALUES (?, ?, ?, ?)
            
        """
    )
    groupData = [(sname, email, sid,  gid)]
    for sname, email, sid, gid in groupData:
        insertIntoStudentQuery.addBindValue(sname)
        insertIntoStudentQuery.addBindValue(email)
        insertIntoStudentQuery.addBindValue(sid)
        insertIntoStudentQuery.addBindValue(gid)

        insertIntoStudentQuery.exec()


def getGroupNames():
    selectquery = QSqlQuery()
    selectquery.exec(
        """
            SELECT groupName 
            FROM GroupTable
        """
    )
    
    
def getGroupMemberNamesFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT StudentTable.studentName FROM StudentTable INNER JOIN GroupTable ON StudentTable.groupId = GroupTable.groupId WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId)    
    cursor.close()

def getGroupNameFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT groupName FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId)  
    group_name = list(cursor.fetchall())
    cursor.close() 
    return group_name[0][0]

def getGroupNumberFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT groupNum FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId)
    cursor.close() 

def getMeetingDayFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT meetingday FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId) 
    cursor.close()

def getMeetingTimeFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT meetingtime FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId) 
    cursor.close()

def getWhichClassFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT whichClass FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId) 
    cursor.close()

def getSectionFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT section FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId) 
    cursor.close()

def getSemesterFromGroupID(groupId):
    groupId = (groupId, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT semester FROM GroupTable WHERE GroupTable.groupId = ?"    
    cursor.execute(query,groupId) 
    cursor.close()

def getStudentEmailFromStudentNameToEdit(studentName):
    studentName = (studentName, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT email FROM StudentTable WHERE StudentTable.studentName = ?"    
    cursor.execute(query,studentName) 
    cursor.close()

def getStudentIdFromStudentNameToEdit(studentName):
    studentName = (studentName, )
    con = sqlite3.connect("SeniorNotes.sqlite")
    cursor = con.cursor()
    query = "SELECT studentId FROM StudentTable WHERE StudentTable.studentName = ?"    
    cursor.execute(query,studentName)
    cursor.close()

def getEditGroupData(primaryKey): # returns ([group], [students])
    connector = sqlite3.connect("SeniorNotes.sqlite")
    cursor = connector.cursor()
    query = "SELECT groupName, groupNum, whichClass, section, semester, meetingday, meetingtime "
    query +="FROM GROUPTABLE "
    query +="WHERE groupId = '" + primaryKey + "'"
    
    cursor.execute(query)
    group = list(cursor.fetchall())

    query = "SELECT studentName , email, studentId "
    query +="FROM StudentTable "
    query +="WHERE groupId = '" + primaryKey + "'"
    cursor.execute(query)
    students = list(cursor.fetchall())   
    cursor.close()
    return (group[0], students)

def getNotesFromGroupID(groupId):
    connector = sqlite3.connect("SeniorNotes.sqlite")
    cursor = connector.cursor()
    query = "SELECT date, notes "
    query +="FROM GroupNotes "
    query +="WHERE groupId = '" + groupId + "'"
    cursor.execute(query)
    notes = list(cursor.fetchall())
    return notes

def getNoteFromDate(groupId, date):
    connector = sqlite3.connect("SeniorNotes.sqlite")
    cursor = connector.cursor()
    query = "SELECT notes "
    query +="FROM GroupNotes "
    query +="WHERE date = '" + date + "'"
    query +="AND groupId = '"+ groupId+"'"
    cursor.execute(query)
    note = list(cursor.fetchall())
    return note[0]

def getStudentInfoFromGroupID(groupId):
    connector = sqlite3.connect("SeniorNotes.sqlite")
    cursor = connector.cursor()
    query = "SELECT studentName, email "
    query +="FROM StudentTable "
    query +="WHERE groupId = '" + groupId + "'"
    cursor.execute(query)
    studentInfo = list(cursor.fetchall())
    return studentInfo

def doesGroupExist(semester, groupname):
    primary_key =(str(semester) + str(groupname)).replace(" ", "")
    connector = sqlite3.connect("SeniorNotes.sqlite")
    cursor = connector.cursor()
    query = "SELECT groupId "
    query +="FROM GROUPTABLE "
    query +="WHERE groupId = '" + primary_key + "'"
    
    cursor.execute(query)
    group = list(cursor.fetchall())
    if(len(group) != 0):
        return True
    return False

# Update all pks
def replaceIntoGroupTable(old_pk, new_pk, groupNum, groupName, meetingday, meetingtime, whichClass, section, semester):
    query = QSqlQuery()
    query.prepare(
        """
            REPLACE INTO GroupTable (groupName, groupNum, meetingday, meetingtime, whichClass, section, semester, groupId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            
        """
    )
    query.addBindValue(groupNum)
    query.addBindValue(groupName)
    query.addBindValue(meetingday)
    query.addBindValue(meetingtime)
    query.addBindValue(whichClass)
    query.addBindValue(section)
    query.addBindValue(semester)
    query.addBindValue(new_pk)
    query.exec()

def removeGroupFromGroupTable(groupId):
    query = QSqlQuery()
    query.prepare(
        """
            DELETE FROM GroupTable 
            WHERE groupId = ?
        """
    )
    query.addBindValue(groupId)
    query.exec()

def removeNotesFromNotesTable(groupId):
    query = QSqlQuery()
    query.prepare(
        """
            DELETE FROM GroupNotes 
            WHERE groupId = ?
        """
    )
    query.addBindValue(groupId)
    query.exec()

def removeNoteFromNotesTable(groupId, date):
    query = QSqlQuery()
    query.prepare(
        """
            DELETE FROM GroupNotes 
            WHERE groupId = ?
            AND date = ?
        """
    )
    query.addBindValue(groupId)
    query.addBindValue(date)
    query.exec()


def removeStudentFromStudentTable(groupId):
    query = QSqlQuery()
    query.prepare(
        """
            DELETE FROM StudentTable 
            WHERE groupId = ?
        """
    )
    query.addBindValue(groupId)
    query.exec()


def removeNotefromGroup(groupId):
    query = QSqlQuery()
    query.prepare(
        """
            DELETE FROM GroupNotes 
            WHERE groupId = ?
        """
    )
    query.addBindValue(groupId)
    query.exec()

# GroupNotes - shouldnt need to touch this one except when updating pk above
def updateGroupNotesIds(old_pk, new_pk):
    query = QSqlQuery()
    query.prepare(
        """
            UPDATE GroupNotes SET groupId = ?
            WHERE groupId = ?
        """
    )
    query.addBindValue(new_pk)
    query.addBindValue(old_pk)
    query.exec()


def updateStudentsTable(old_pk, new_pk, students):
    query = QSqlQuery()
    query.prepare(
        """
            DELETE FROM StudentTable
            WHERE groupId = ?
        """
    )
    
    query.addBindValue(old_pk)
    
    query.exec()
    for student in students:
        insertintoStudent(student[0], student[1], student[2], new_pk)

    # query.prepare(
    #     """
    #         UPDATE StudentTable SET groupId = ?
    #         WHERE groupId = ?
    #     """
    # )
    # query.addBindValue(new_pk)
    # query.addBindValue(old_pk)

    # query.exec()

def updateNoteFromDate(groupId, date, note):
    query = QSqlQuery()
    query.prepare(
        """
            UPDATE GroupNotes SET notes = ?
            WHERE groupId = ?
            AND date = ?
        """
    )
    query.addBindValue(note)
    query.addBindValue(groupId)
    query.addBindValue(date)
    query.exec()


    # success = QtWidgets.QMessageBox()
    # success.setText("Success! Group has been updated. " )
    # success.setWindowTitle("Group Updated!")
    # success.setStandardButtons(QtWidgets.QMessageBox().Ok)
    # success.exec()

        
        

