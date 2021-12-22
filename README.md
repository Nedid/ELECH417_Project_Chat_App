# ELECH417_Project_Chat_App
Chat App Project for Communication Networks course

Server-based chat app coded in python as project for Communication Networks course.
Allows encrypted communication between users identifying through an account.
Works only on local nework due to lack of free available central server (theorically would work on it)
 
Steps to run the project:

- Make sure to have Python installed as well as the following packages :
	- tkinter
	- cryptography
	- socket
	- threading
	- sys
	- sqlite3

You can download the different packages in the command window with the following line:
- On Unix/macOS: python3 -m pip install InsertPackageName
- On Windows: py -m pip install InsertPackageName

If you have any trouble for the installation, you can consult these websites:

https://www.python.org/downloads/
https://packaging.python.org/en/latest/tutorials/installing-package

- First, run the main file on the server folder. A window should appear.
 Click on the "Open server" button. A message should confirm you that the server is running.
 Note that there might be issues on Linux or Mac devices as all tests were running on Windows.

- Next, run the main file of the client folder. You can run as many client as you want, on
 whatever device that is connected to you private network.

- If you do not have an account, create one by cliking on "Sign up". A new window should appear
 where you can choose your username and password. If you already have an account, you can 
 direclty put your username and password in the "Log in" window. Then press the login button
 or simply press the 'Enter' key on your keyboard on the password cell.

- If your informations are valid, you will be led to a chat window. To make a conversation, first
 click on the "Friend List" button. A new window should appear. You have 2 options:
	- Above, consult your friend list and start a conversation with one of them
	- Below, add new friends by their username
 Note that to start a conversation, both users should be friend with each other, meaning that 
 both must send a friend request to the other. Also, they need to be connected at the same time
 to be able to send messages.

- Start your conversation, you can add emotes by clicking on the "emote" button. There are various
 emotes you can select in the dedicated pannel and add them directly to your messages.

- When you are done, simply exit the client application and close the server with the dedicated button
 on the server window.

- With the database, any information should be restored when you log in the next time.
