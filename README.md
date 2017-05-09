# Item-Catalog

## Instrucitons to Run Project

### Set up a Google Plus auth application.
1. go to https://console.developers.google.com/project and login with Google.<br>
2. Create a new project<br>
3. Name the project<br>
4. Select "API's and Auth-> Credentials-> Create a new OAuth client ID" from the project menu<br>
5. Select Web Application<br>
6. On the consent screen, type in a product name and save.<br>
7. In Authorized javascript origins add:<br>
    http://localhost:5000<br> 
8. Click create client ID<br>
9. Click download JSON and save it into the root director of this project.<br> 
10. Rename the JSON file "client_secret.json"<br>
11. In index.html place your client id "data-clientid="yourclienid" so that it uses your Client ID from the web applciation. <br>

### Setup the Database & Start the Server
1. In the root director, use the command vagrant up<br>
2. The vagrant machine will install.<br>
3. Once it's complete, type vagrant ssh to login to the VM.
4. In the vm, cd /vagrant
5. type "pyhon database_setup.py" this will create the database with the categories defined in that script.Please Note SQLite database is used here.SQLite database is inbuild with python.
6. type "python main.py" to start the server.

### Open in a webpage
1. Now you can open in a webpage by going to :
    http://localhost:5000

