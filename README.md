# AdhesionLab
If you are reading this document you are likely doing adhesion research with Helen! As you may know, most of the work we do in this lab relies on code. What kinds of experiments we are running and the kinds of data analysis we are doing is always changing and evolving, and in turn the code also changes. This GitHub repository exists in order to keep track of all this code and the modifications made to it. Because of the nature of this lab there is a wide range of familiarity with computer science and collaborative coding workflows. I will do my best to write this in such a way that if something does not make sense then you have enough information to google your way to an answer. If you are interested in writing code and/or modifying existing code (rather than just using existing code), and you are not familiar with Git and GitHub I suggest reading the resources below that I found helpful when learning about these things:

[Getting Started with Git](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)

[Getting Started with GitHub](https://docs.github.com/en/get-started)

**Disclaimer:** Although this repository was created by me, the code within has been contributed to by many people before being put into this repository. The code for the adhesion lab is a very collaborative endeavor and it has taken many peoples’ time and energy to make all of this happen.

## How is this repository organized?
On the main branch there are three folders: Levelling_Table, Test_Running, and Test_Analysis. Each of these folders contain code corresponding to a different part of the data collection process: 
1. Levelling_Table - contains code that enables communication between the arduino, the attached electronics, testXpert, and python scripts while levelling is occuring.
2. Test_Running - contains python scripts that are used to run tests. If you want to understand how to run tests using these scripts on the lab computer refer to the [Probe Tack Test S.O.P](https://docs.google.com/document/d/1UmUZKZvCBH7tiiC7ttzYZqN0IUQPj35D1J8YuI-1PR8/edit) in the Research Google Drive.
3. Test_Analysis - this folder has the most files and it is the most varied. Any code that has been written to process or analyze collected data in one way or another can be found here.

In addition to the main branch there is also a branch named "AnalysisGUI." This branch has a graphical user interface (GUI) that can be used to sync video and force-displacement data from the tensile tester. The GUI works, but it is clunky, and poorly optimized. Because of this, it lives in its own branch. If optimized, and perhaps rewritten with a new framework, this could be a very useful tool for data analysis (and it could find a home in the main branch)

## How can I use this repository?
GitHub repositories have countless features and ways to interact with them and it can be rather overwhelming to parse everything and to do simple things. In this section I aim to describe how you can use the repository in the context of adhesive research with Helen. I will present the two main ways I envision the repository being used and the most important things to know for each of these use cases. 
### Using the repository to run up to date code
Although writing the code contained within this repository is quite fun, the real reason all of this exists is so that we can run tests, collect data, and analyze it. The repository should contain up to date and functioning code necessary to do all of this. Because of this even if you do not intend to write any code and just want to do fun sciencey stuff you will (ideally) interact with this repository, and use it to ensure that you are running the right version of the code. The easiest way to to make sure you are running up to date code is to use the github desktop application to sync files on your computer with those on this repository. Below are some resources to help getting started with the github desktop application and syncing to a repository:

https://docs.github.com/en/desktop/overview/getting-started-with-github-desktop

https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/syncing-your-branch-in-github-desktop

Some of the scripts ask the user to input the directory of a data file. While it is possible, to download files on a case by case basis from the google drive, the easier method is to use the google drive desktop [application](https://www.google.com/drive/download/). This application will allow you to access all files on the drive as if they were located on your own computer.  

To run the scripts you will  need to have python and the following python packages installed:
1. [numpy](https://numpy.org/)
2. [pandas](https://pandas.pydata.org/)
3. [matplotlib](https://matplotlib.org/)
4. [openCV-python](https://pypi.org/project/opencv-python/)
5. [tkinter](https://docs.python.org/3/library/tkinter.html)

Most scripts only use a subset of these packages, so if you only need to use one script, the `import` at the top of script's code should indicate what you need to have installed. 
