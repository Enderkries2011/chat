# Mesage (For Images "https://github.com/Enderkries2011/chat.assets")
A Simple Flask Hosted Messaging Service

# Features
1. File Upload/Download ('png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'pdf')
2. Messaging (Works like a groupchat, NO INDIVIDUAL CHATS)
3. Accounts (Google Spreadsheet)
4. Chat Colors
5. Instant login

# Spreadsheet Database
How it should Look:

![image](https://github.com/user-attachments/assets/6966b1cb-eafc-4421-8927-b276ed8ea9ef)

The Authcode field make this link work (http://0.0.0.0/login?email=1@example.com&authcode=1234),
u can attach it in a email and u dont have to type a password to log in.

The Email field is used to login just like the Password Field.

The Color Field u can choose what color which person chats in.

The Username field is for what name that person should chat with.

# How to setup
1. Make A Spreadsheet (like i showed Above)
2. Create google drive&sheets api
3. Download Api Credentials File (Move into the root directory of your code & Make sure it looks like "api-example.json")
4. dowload code
5. edit server.py (Google Sheets configuration & app.secret_key)
6. install requirements.txt
7. start server.py
8. Test to see if it works (http://YourIpAddress:80 | You do not need to add the 80 cause its http default)

# Bugs
For now the only bug i know of is that if u login with the authcode u cant send files
