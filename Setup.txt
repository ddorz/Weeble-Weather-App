Setting up and running the project


Setting up a virtual env and installing mysqlclient
1.  Open a terminal and run pip install virtualenv
2.  Navigate to the project directory
3.  Run virtualenv Weeble
4.  Activate the env with .\Weeble\venv\Scripts\activate
5.  Run pip install django
6.  Download mysql-1.3.13 from http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python
7.  Move the .whl file into your project directory
8.  Run pip install mysqlclient-1.3.13-cp37-cp37m-win_amd64.whl 
9.  Run pip install mysql-connector-python

Installing MySQL Server 8.0
1. Download and install Microsoft Redistribute C++ 2013 x86 and x64
	- Download x86 and x64 setups: https://www.microsoft.com/en-us/download/details.aspx?id=40784
2. Install both x86 and x64 versions
3. Download MySQL installer from https://dev.mysql.com/downloads/installer/
4. Run MySQL installer and complete setup with default options. When you reach the MySQL server configuration page, set the root password as: toor
5. Verify mysql has been added to PATH: 
	- Open a file explorer and right click ‘Computer’ then select ‘Properties’
	- Select ‘Advanced system settings’ then ‘Environment Variables’
	- Under ‘System variables’ select ‘New’ then enter MYSQL_HOME in ‘Variable name’ and C:\Program Files\MySQL\MySQL Server 8.0\bin in ‘Variable value’ (change this path if you used a different installation directory)
	- Highlight ‘Path’ under ‘User variables’ and select edit. Move your cursor to the end of ‘Variable value’ and add a semicolon then %MYSQL_HOME%
	- Hit ‘OK’ 

Creating Weeble database tables
1.  Open a terminal 
2.  Enter mysql -u root -p
3.  Enter password (toor) and hit enter
4.  Run mysql> CREATE DATABASE weeble;
5.  Run mysql> USE weeble;
6.  CREATE TABLE Users (
	user_id INT NOT NULL AUTO_INCREMENT,
	UserName VARCHAR(30) NOT NULL,
	Password VARCHAR(30) NOT NULL,
	Email VARCHAR(30) NOT NULL,
	RegistrationDate DATE NOT NULL,
	isPremium BIT,
	LastLoginDate DATE,
	PRIMARY KEY (user_id)
); 
7.  Run mysql> CREATE TABLE PremiumUsers (
	userName INT NOT NULL,
	PremiumUserID INT NOT NULL AUTO_INCREMENT,
	FirstCity VARCHAR(30),
	SecondCity VARCHAR(30),
	ThirdCity VARCHAR(30),
	FourthCity VARCHAR(30),
	FifthCity VARCHAR(30),
	APICalls INT NOT NULL,
	LastResetDate DATETIME NOT NULL,
	PRIMARY KEY (PremiumUserID)
);
8.  Run mysql> CREATE TABLE FreeUsers (
	userName INT NOT NULL,
	FreeUserID INT NOT NULL AUTO_INCREMENT,
	FirstCity VARCHAR(30),
 	APICalls INT NOT NULL,
	LastResetDate DATETIME NOT NULL,
	PRIMARY_KEY(FreeUserID)
);
9.  Run mysql> USE weeble;
10. Run mysql> CREATE USER 'djangouser'@'localhost' IDENTIFIED BY 'toor';
11. Run mysql> GRANT ALL ON django.* TO 'djangouser'@'localhost';

Installing dependencies
1. pip install requests
2. pip install geopy
3. pip install mysqlclient (this needs to be done manually using Python 3.7, see mysql-django-steps.text)
4. pip instal mysql-connector-python

Running the project
1. From the project directory, run: python manage.py runserver 8000
2. Open the link from the console 
3. Sign up as a new user
4. Use the email activation from the console to activate the account
5. You will now be logged in and able to use the application