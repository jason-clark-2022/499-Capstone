from concurrent.futures import wait
from email.headerregistry import Group
import sqlite3
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp, QTimer
from PyQt5.QtGui import QRegExpValidator
from database import *
from datetime import datetime
import database
from mainMenu import Ui_MainWindow


class Main_Menu(QMainWindow, Ui_MainWindow):
    group_manager_pk_storage = ""   # Need to store the pk for editing groups
    last_selected_pk = ""   # last primary key from selection on group table
    date_note_to_edit = ""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        
        
        ############# GENERAL VIEW INITIALIZERS ########################
        self.notesTable.horizontalHeader().setVisible(True)
        self.group_number.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        self.class_section.setValidator(QRegExpValidator(QRegExp("[0-9]*")))

        header_members = self.members_table.horizontalHeader()  
        header_members.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_members.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_members.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header_members.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header_members.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header_members.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        

        header_group_info = self.group_info_table.horizontalHeader()  
        header_group_info.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_group_info.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_group_info.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header_group_info.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.group_info_table.resizeRowsToContents()
        self.group_info_table.resizeColumnsToContents()

        header_notes = self.notesTable.horizontalHeader()  
        header_notes.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_notes.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_notes.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header_notes.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.notesTable.setWordWrap(True)
        self.notesTable.resizeRowsToContents()
        self.notesTable.setSortingEnabled(True)
        

        header_group = self.group_table.horizontalHeader()  
        header_group.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header_group.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_group.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header_group.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        

        ############ GROUP VIEWER INITIALIZERS ########################
        self.edit_group_btn.setEnabled(False)   # Disabled by default, enable when group is selected
        self.group_table.selectionModel().selectionChanged.connect(self.group_table_selection_listener)  #Event listener to see if data within the table is selected
        self.notesTable.selectionModel().selectionChanged.connect(self.note_table_selection_listener)
        self.new_group_btn.clicked.connect(lambda: self.swap_groups_view(False))  #Event listener for Create Group button will take to new screen for group creation
        self.edit_group_btn.clicked.connect(lambda: self.swap_groups_view(True))      #Event listener for Edit Group button will take to new screen for editing groups
        self.remove_group_btn.clicked.connect(self.group_delete_row) #Event listener for Delete Group button
        
        self.refresh_group_table()

        ############ GROUP MANAGER INITIALIZERS #######################

        self.cancel_btn.clicked.connect(self.swap_groups_view)
    
        self.submit_group_btn.setEnabled(False)
        self.group_name.textChanged.connect(self.enableButton)
        self.group_number.textChanged.connect(self.enableButton)
        self.class_number.textChanged.connect(self.enableButton)
        self.class_section.textChanged.connect(self.enableButton)
        self.class_semester.textChanged.connect(self.enableButton)

        self.add_members_btn.clicked.connect(self.add_row)
        selected = self.members_table.selectedItems()
        self.delete_members_btn.clicked.connect(self.student_delete_row)

        

        self.submit_group_btn.clicked.connect(self.submit_group_to_db)
        
        ############ NOTES TAB INITIALIZERS #######################
        self.create_note_button.setEnabled(False)
        self.note_txt.textChanged.connect(self.enablesavenote)
        self.create_note_button.clicked.connect(self.create_new_note_for_db)
        self.remove_note_button.clicked.connect(self.delete_note)
        self.edit_note_button.clicked.connect(self.edit_note)
        
    
    ################# DATABASE MODIFIERS #####################
    def submit_group_to_db(self):
        semester = self.class_semester.text()
        groupname = self.group_name.text()

        if(self.group_manager_pk_storage == ""):    # If create group
            if(database.doesGroupExist(semester, groupname)):
                self.group_manager_pk_storage = (semester + groupname).replace(" ", "")
                self.update_group_db()
            else:
                self.push_group_to_db()

        else:
            self.update_group_db()


    def update_group_db(self):
        # get group relevant information
        group_name = self.group_name.text()
        group_number = int(self.group_number.text())
        meeting_day = self.meeting_day.currentText()
        class_num = self.class_number.text()
        meeting_time = self.meeting_time.time()
        class_sec = self.class_section.text()
        class_sem = self.class_semester.text()
        new_group_pk = (class_sem + group_name).replace(" ", "")
        
        # get student table information
        students = []  
        for row in range(0, self.members_table.rowCount()):
            s_name = self.members_table.item(row, 0).text()
            s_email = self.members_table.item(row, 1).text()
            s_id = self.members_table.item(row, 2).text()
            students.append((s_name, s_email, s_id))

        
        database.replaceIntoGroupTable(self.group_manager_pk_storage, new_group_pk, group_name, group_number, meeting_day, meeting_time, class_num, class_sec, class_sem)
        if(new_group_pk != self.group_manager_pk_storage):
            removeGroupFromGroupTable(self.group_manager_pk_storage) # If the pk changed, remove old data
        updateGroupNotesIds(self.group_manager_pk_storage, new_group_pk)
        updateStudentsTable(self.group_manager_pk_storage, new_group_pk, students)
        success = QMessageBox()
        success.setText("Group Updated")
        success.setWindowTitle("Success!")
        success.setStandardButtons(QMessageBox.Ok)
        #success.exec()
        retval = success.exec()
        if retval == QMessageBox.Ok:
            self.refresh_group_table()
            self.groups_stack.setCurrentIndex(0)





    def push_group_to_db(self):
        groupname = self.group_name.text()
        groupnumber = self.group_number.text()
        classnum = self.class_number.text()
        classsec = self.class_section.text()
        classsem = self.class_semester.text()
        meetingday = self.meeting_day.currentText()
        meetingtime = self.meeting_time.time()
        rowCount = self.members_table.rowCount()
        gid = (classsem + groupname).replace(" ", "")
        insertintoGroup(groupname, groupnumber, meetingday, meetingtime, classnum, classsec, classsem, gid)
        for row in range(0,rowCount):
            insertintoStudent(self.members_table.item(row, 0).text(), self.members_table.item(row, 1).text(), self.members_table.item(row, 2).text(), gid)
        success = QMessageBox()
        success.setText("Group Created")
        success.setWindowTitle("Success!")
        success.setStandardButtons(QMessageBox.Ok)
        #success.exec()
        retval = success.exec()
        if retval == QMessageBox.Ok:
            self.refresh_group_table()
            self.groups_stack.setCurrentIndex(0)

    def create_new_note_for_db(self):
        date = datetime.now() 
        dt_string = date.strftime("%m/%d/%Y %H:%M:%S")
        note = self.note_txt.toPlainText()
        
        try:
            if(self.last_selected_pk == ""):  
                raise ValueError("No group selected")
            if(self.date_note_to_edit == ""):
                insertintoNotes(dt_string, note, self.last_selected_pk)
            else:
                updateNoteFromDate(self.last_selected_pk, self.date_note_to_edit, note)
            self.date_note_to_edit = ""
            self.populate_notes()
            noteAdded = QMessageBox()
            noteAdded.setText("Note has been added to group " + self.last_selected_pk)
            noteAdded.setWindowTitle("Note Added!")
            noteAdded.setStandardButtons(QMessageBox.Ok)
            noteAdded.exec()
            self.note_txt.clear()

        except:  
            selectGroup = QMessageBox()
            selectGroup.setText("Please select a group to add a note to.")
            selectGroup.setWindowTitle("Error- No group selected!")
            selectGroup.setStandardButtons(QMessageBox.Ok)
            selectGroup.exec()

    def delete_note(self):
        sm = self.notesTable.selectionModel()
        if sm.hasSelection():
            buttonyes = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this note?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)       
            if(buttonyes == QMessageBox.Yes):
                selected_row = self.notesTable.selectedItems()
                database.removeNoteFromNotesTable(self.last_selected_pk, selected_row[0].text())
                self.populate_notes()

    def edit_note(self):
        selected_row = self.notesTable.selectedItems()
        date = selected_row[0].text()
        self.date_note_to_edit = date
        self.note_txt.clear()
        self.note_txt.setText(selected_row[1].text())
        self.note_prompt.setText("Editing note from " + date)
        
        # database.removeNoteFromNotesTable(self.last_selected_pk, date)
                



    ############ GENERAL GROUPS_INFO STUFF ########################
    def update_selected_group_label(self):
        if(self.last_selected_pk == ""):
            self.last_selected_group_label.setText("Select a group") 
        else:            
            text = "Group: "
            text += getGroupNameFromGroupID(self.last_selected_pk)
            self.last_selected_group_label.setText(text)


    ############ GENERAL GROUPS_STACK STUFF ########################
    """ Switches the current page for groups_view, 
        Populate parameter determines if the text fields should be filled (use when editing group) 
    """
    def swap_groups_view(self, edit_group): 
        if(self.groups_stack.currentIndex() == 0): 
            self.clear_group_manager_fields()
            if(edit_group):  
                self.group_manager_pk_storage = self.get_selected_grouptable_pk()   # store this for updating db
                self.title_label.setText("Edit Group")
                self.populate_group_manager_fields()


            else:  
                self.title_label.setText("Create Group")
                
            self.groups_stack.setCurrentIndex(1)
        else:   
            self.group_manager_pk_storage = ""
            self.refresh_group_table()
            self.groups_stack.setCurrentIndex(0)
        



    ############### GROUP VIEWER METHODS ############################

    def note_table_selection_listener(self):
        sm = self.notesTable.selectionModel()
        if sm.hasSelection():
            self.remove_note_button.setEnabled(True)
            self.edit_note_button.setEnabled(True)
            self.date_note_to_edit = ""
            self.note_txt.clear()
            self.note_prompt.setText("Enter New Note Below")
        else:
            self.remove_note_button.setEnabled(False)
            self.edit_note_button.setEnabled(False)

    """ This method will be signaled every time a different row in the table is selected """
    def group_table_selection_listener(self):
        sm = self.group_table.selectionModel()
        
        if sm.hasSelection():
            self.last_selected_pk = self.get_selected_grouptable_pk()
            self.update_selected_group_label()
            self.populate_notes()
            self.populate_group_info()        
            self.edit_group_btn.setEnabled(True)
            self.remove_group_btn.setEnabled(True)
            self.date_note_to_edit = ""
            self.note_txt.clear()
            self.note_prompt.setText("Enter New Note Below")
        else:
            self.last_selected_pk = ""
            self.update_selected_group_label()
            self.populate_notes()
            self.populate_group_info()
            self.edit_group_btn.setEnabled(False)
            self.remove_group_btn.setEnabled(False)
            
    
    """ returns the primary key of the currently selected row in a table """
    def get_selected_grouptable_pk(self, col_of_semester=4, col_of_groupname=1):
        sm = self.group_table.selectionModel()
        if sm.hasSelection():
            selected_row = self.group_table.selectedItems()
            if(len(selected_row) > max(col_of_groupname, col_of_semester)): # make sure in bounds
                row_data = [data.text() for data in selected_row]
                return (row_data[col_of_semester] + row_data[col_of_groupname]).replace(" ", "")
        return ""

    """ when called, method removes all data from table and requeries the database for new data"""
    def refresh_group_table(self):
        self.group_table.setRowCount(0) # remove all data in table
        row_index = 0   # index where row will be inserted
        
        # --- start query ---
        connector = sqlite3.connect("SeniorNotes.sqlite")
        cursor = connector.cursor()
        query = "SELECT groupNum, groupName, whichClass, section, semester FROM GROUPTABLE"
        cursor.execute(query)
        groups = list(cursor.fetchall())
        # --- end query ---
        
        
        # table cols
        # Group Number | Group Name | Class | Section | Semester | ID
        for group in groups: 
            self.group_table.insertRow(row_index) # Create a new row to populate

            for col_num in range(len(group)):
                item = QTableWidgetItem(str(group[col_num]))  # Int values need to be casted to string
                item.setFlags(item.flags() &~ QtCore.Qt.ItemIsEditable) # "|" = enable flag, "&~" = disable flag
                self.group_table.setItem(row_index, col_num, item) 
                
            row_index += 1 # This will keep default order based on which groups were enterd first

        header_group = self.group_table.horizontalHeader()  
        header_group.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header_group.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header_group.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_group.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header_group.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
    

    ############### GROUP MANAGER METHODS ############################

    """ Check to see if all fields in submission form are full before submitting"""   
    @QtCore.pyqtSlot()    
    def enableButton(self):
        if(self.group_manager_pk_storage == ""):
            if(database.doesGroupExist(self.class_semester.text(), self.group_name.text())):
                self.submit_group_btn.setText("Update Group")
            else:
                self.submit_group_btn.setText("Create Group")
        else:
            self.submit_group_btn.setText("Update Group")
        self.submit_group_btn.setEnabled(bool(self.group_name.text()) and bool(self.group_number.text()) and bool(self.class_number.text()) and bool(self.class_section.text()) and bool(self.class_semester.text()))

    # @QtCore.pyqtSlot()
    def enablesavenote(self):
        self.create_note_button.setEnabled(bool(self.note_txt.toPlainText()))       

    """ Adds row to student_table"""
    def add_row(self):
        rowCount = self.members_table.rowCount()
        self.members_table.insertRow(rowCount)
        self.members_table.setItem(rowCount, 0, QTableWidgetItem("Enter Student Name"))
        self.members_table.setItem(rowCount, 1, QTableWidgetItem("Enter Student Email"))
        self.members_table.setItem(rowCount, 2, QTableWidgetItem("Enter Student ID"))

    """ Removes row from student_table"""
    def student_delete_row(self):
        self.members_table.removeRow(self.members_table.currentRow())
    
    """ Removes row from group_table"""
    def group_delete_row(self):
        buttonyes = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this group?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)       
        if(buttonyes == QMessageBox.Yes):
            database.removeGroupFromGroupTable(self.last_selected_pk)
            database.removeNotesFromNotesTable(self.last_selected_pk)
            database.removeStudentFromStudentTable(self.last_selected_pk)
            self.group_table.clearSelection()
            self.refresh_group_table()


    """ populate the fields on the group_manager screen with input from database"""
    def populate_group_manager_fields(self):  # Fill all input fields on edit group screen    
        self.clear_group_manager_fields()
        main = widget.widget(0)
        grouptable_pk = main.get_selected_grouptable_pk()
        group, students = database.getEditGroupData(grouptable_pk)
        
        
        # groups = [groupName | groupNum | whichClass | section | semester | meetingday | meetingtime]
        if(len(group) >= 7):
            self.group_name.setText(str(group[0]))  
            self.group_number.setText(str(group[1]))
            self.class_number.setText(str(group[2]))
            self.class_section.setText(str(group[3]))
            self.class_semester.setText(str(group[4]))
            self.meeting_day.itemText(self.meeting_day.findText(str(group[5])))
            # time = QtCore.QTime.fromString(str(group[6]))
            self.meeting_time.setTime(QtCore.QTime.fromString(str(group[6])))
        
        # students = [studentName | email | studentId]
        if(len(students) >= 1):
            row_count = 0
            for student in students:
                self.members_table.insertRow(row_count)
                self.members_table.setItem(row_count, 0, QTableWidgetItem(student[0]))
                self.members_table.setItem(row_count, 1, QTableWidgetItem(student[1]))
                self.members_table.setItem(row_count, 2, QTableWidgetItem(str(student[2])))
                row_count += 1

        header_group_info = self.group_info_table.horizontalHeader()  
        header_group_info.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_group_info.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_group_info.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header_group_info.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.group_info_table.resizeRowsToContents()

    """ Clear all data fields from group_manager screen"""
    def clear_group_manager_fields(self):
        self.group_name.clear()
        self.group_number.clear()
        self.class_number.clear()
        self.class_section.clear()
        self.class_semester.clear()
        # self.meeting_day.clear()
        self.members_table.setRowCount(0)

    ############### NOTES TAB METHODS ############################
    """ re-writes all relevent information into the notes_table"""
    def populate_notes(self):
        self.notesTable.setSortingEnabled(False)
        self.notesTable.setRowCount(0)  
        notes = database.getNotesFromGroupID(self.last_selected_pk)
        
        

        if(len(notes) >= 1 and self.last_selected_pk != ""):
            row_count = 0
            for note in notes:
                self.notesTable.insertRow(row_count)
                self.notesTable.setItem(row_count, 0, QTableWidgetItem(note[0]))
                self.notesTable.setItem(row_count, 1, QTableWidgetItem(note[1])) 
        
        header_notes = self.notesTable.horizontalHeader()  
        header_notes.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_notes.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_notes.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header_notes.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.notesTable.setWordWrap(True)
        self.notesTable.resizeRowsToContents()
        self.notesTable.setSortingEnabled(True) 
                
        




    ############### GROUP INFO TAB METHODS ############################
    """ re-writes all relevent information into the group_info_table"""
    def populate_group_info(self):
        self.group_info_table.setRowCount(0)  
        group = database.getStudentInfoFromGroupID(self.last_selected_pk)
        
        
        if(len(group) >= 1 and self.last_selected_pk != ""):
            row_count = 0
            for student in group:
                self.group_info_table.insertRow(row_count)
                self.group_info_table.setItem(row_count, 0, QTableWidgetItem(student[0]))
                self.group_info_table.setItem(row_count, 1, QTableWidgetItem(student[1]))   

        self.notesTable.setWordWrap(True)
        self.notesTable.resizeRowsToContents()
 




####### MAIN #######
if __name__ == "__main__":
    app = QApplication(sys.argv)     

    #creating objects for each widget
    main = Main_Menu()


    #creating widget stack
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(main) #index 0

    widget.show()
    try:
        sys.exit(app.exec())
    except:
        print("exiting")