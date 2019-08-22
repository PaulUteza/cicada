------------
Introduction
------------

CICADA stands for Calcium Imaging Complete Automated Data Analysis.

It's a Python pipeline aimed for analyzing calcium imaging data. 

Motivation
""""""""""
We notice a lack of toolboxes or analysis pipelines for calcium imaging data, using open source language. 
Our motivation was to build an easy-to-use pipeline, which doesn't need programming skills. 
In that purpose, we offer a Graphical User Interface as well as a command line usage.

In order to tackle the broadness of scientists' needs, we built the pipeline to be easily extendable with a plugin-like interface, for data format and analyses.  


Supported data format
"""""""""""""""""""""

The default data format chosen was Neurodata Without Borders: Neurophysiology (NWB:N) that is a data standard for neurophysiology, providing neuroscientists with a common standard to share, archive, use, and build analysis tools for neurophysiology data. NWB:N is designed to store a variety of neurophysiology data, including data from intracellular and extracellular electrophysiology experiments, data from optical physiology experiments, and tracking and stimulus data.(https://www.nwb.org/)

We provide some tools to convert their data into NWB, with a plugin-like interface (see github address)


Functionalities
"""""""""""""""
- We offer a Graphical User Interface (GUI) as well as a command line usage.
- We have already implemented or aim to implement various kind of analyses such cell assemblies detection, network analyses, display functions (rasters, cells map) etc...
- The GUI offers specifics functionalities:
  - Subject and recorded sessions can be filtered or grouped in order to easily select the data to be analysed, and saved for future use.
  - Analyses are grouped by family. Each analysis provide a way to check the data see if they are compatible. 
  - Analyses arguments can be saved in a yaml file allowing to easily load them later. 
  - A multi-thread implementation allows multiple analysis at the same time. 
  - A progression bar allows to follow the analysis current status. 

