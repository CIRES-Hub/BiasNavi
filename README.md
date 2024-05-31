# BiasNavi
A data bias management toolkit developed by ARC Training Centre for Information Resilience [CIRES](https://cires.org.au/).

BiasNavi aims to manage the bias in datasets. It complies with the following pipeline:

+ **Identifying**: Identify if the data or system being used is subject to bias or fairness issues. 
+ **Measuring**: Quantify with an appropriate metric the magnitude of different types of bias present in the data or system being considered. 
+ **Indexing**: Collect, parse, structure, and store bias metadata and fairness policies aimed at facilitating a subsequent fast and effective retrieval and system adaptation. 
+ **Surfacing**: Present in an appropriate way to the end user the bias present in the underlying data and/or any fairness policy that have been applied to the data or system under consideration. 
+ **Adapting**: Provide the user with a set of tools that allows them to interact with existing biased results and to adapt them for bias in their preferred ways.

## Architecture
<img src="architecture.png" alt="architecture" width="600">

## Easy Setup
1. Download the project
2. Run pip install -r requirements. txt in your terminal to install all the depencenies.
3. Config your API key in the file of Config.ini under the root directory of the project.
4. Run python main.py to start the program.
