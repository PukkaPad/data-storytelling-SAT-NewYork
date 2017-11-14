New York SAT - Storytelling Project
-----------------------

Data cleaning, exploration and visualization for the SAT New York city public schools.


Installation
----------------------

### Download the data

* Clone this repo to your computer.
* Get into the folder using `cd data-cleaning-SAT-NewYork`.
* Run `mkdir data`.
* Switch into the `data` directory using `cd data`.
* Download the data files into the `data` directory.
    * You can find the data here
        * [SAT](https://data.cityofnewyork.us/Education/SAT-Results/f9bf-2cp4)
        * [School attendance](https://data.cityofnewyork.us/Education/School-Attendance-and-Enrollment-Statistics-by-Dis/7z8d-msnt)
        * [Math test results](https://data.cityofnewyork.us/Education/NYS-Math-Test-Results-By-Grade-2006-2011-School-Le/jufi-gzgp)
        * [Class size](https://data.cityofnewyork.us/Education/2010-2011-Class-Size-School-level-detail/urz7-pzb3)
        * [AP test results](https://data.cityofnewyork.us/Education/AP-College-Board-2010-School-Level-Results/itfs-ms3e)
        * [Graduation outcomes](https://data.cityofnewyork.us/Education/Graduation-Outcomes-Classes-Of-2005-2010-School-Le/vh2h-md7a)
        * [Demographics](https://data.cityofnewyork.us/Education/School-Demographics-and-Accountability-Snapshot-20/ihfw-zy9j)
        * [School survey](https://data.cityofnewyork.us/Education/NYC-School-Survey-2011/mnz3-dyi8)
            * The above will be downloaded as `.zip` file. Extract the zip file and rename the directory to 'survey'.
        * [High School Directory](https://data.cityofnewyork.us/Education/DOE-High-School-Directory-2014-2015/n3p6-zve2)
        * [School district maps](https://data.cityofnewyork.us/Education/School-Districts/r8nu-ymqj)
            * Click on 'Export' and download as 'GeoJSON'
* Switch back into the `data-cleaning-SAT-NewYork` directory using `cd ..`

### Install the requirements

* Install the requirements using `pip install -r requirements.txt`.
    * You may want to use a virtual environment for this.

api
----------------------
* Create a virtual environment in which Flask and all the necessary libraries will be installed
    * `mkdir api_development`
    * `cd api_development`
    * For Python 2.x: `virtualenv venv`
    Note: Install the requirements were saved in `requirements.txt`
* Run:
    * `source venv\bin\activate`
    (make sure the directory is `api_development`)
    * python server.py


dashboard
----------------------

* Create a virtual environment in which Flask and all the necessary libraries will be installed
    * `mkdir daskboard`
    * `cd dashboard`
    * For Python 2.x: `virtualenv flask`
* Install:
    * `flask/bin/pip install flask`
    * `flask/bin/pip install pandas`
    * `flask/bin/pip install bokeh`
* Run:
    * `source flask\bin\activate`
    (make sure the directory is `dashboad`)
    * `chmod a+x views.py`
    * `./views.py`
