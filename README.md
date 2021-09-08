# tableau-portfolio

This project shows how the mock-up data was created and structured for my Tableau portfolio dashboard.

If you want to check out how the dashboard looks like and interact with it (by using the filters or checking the tooltips and actions), click on this URL here: [Tableau Public - Marketing Dashboard by Renato Rossi](https://public.tableau.com/views/MarketingDashboard_16306994865670/MarketingDashboard-CustomerJourney?:language=en-US&:display_count=n&:origin=viz_share_link "Click to see the dashboard")

Also, if you want to send me questions or suggestions, don't hesitate to send me a message on [my LinkedIn](https://www.linkedin.com/in/renatorossi1/?locale=en_US "Click to access Renato Rossi's LinkedIn profile").

![Marketing Dashboard - Customer Journey](https://raw.githubusercontent.com/renaros/tableau-portfolio/main/Marketing%20Dashboard%20-%20Customer%20Journey.png "First screen containing customer journey related information")

![Marketing Dashboard - Customer Activity](https://raw.githubusercontent.com/renaros/tableau-portfolio/main/Marketing%20Dashboard%20-%20Customer%20Activity.png "Second dashboard containing customer activity related information")


## How to run the project on your own:

Create a new virtual environment

`python3 -m venv /<path_to_project_folder>/tableau-portfolio/venv`

Activate the virtual environment:

`source /<path_to_project_folder>/tableau-portfolio/venv/bin/activate`

Download dependencies:

`pip install faker`

`pip install pandas`

Go to the project folder and open the file **main.py**. Edit the parameters available, setting from which date you want to start populating your fake database (months back) and the number of customers to be created. Save the file.

After changing the file, run the following command to execute the code:

`python3 ./main.py`

This will trigger the process and create all source files inside the output folder.