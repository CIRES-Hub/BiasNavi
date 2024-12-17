# BiasNavi
A data bias management toolkit developed by ARC Training Centre for Information Resilience [CIRES](https://cires.org.au/).

BiasNavi aims to manage the bias in datasets. It complies with the following pipeline:

+ **Identifying**: Identify if the data or system being used is subject to bias or fairness issues. 
+ **Measuring**: Quantify with an appropriate metric the magnitude of different types of bias present in the data or system being considered. 
+ **Surfacing**: Present in an appropriate way to the end user the bias present in the underlying data and/or any fairness policy that have been applied to the data or system under consideration. 
+ **Adapting**: Provide the user with a set of tools that allows them to interact with existing biased results and to adapt them for bias in their preferred ways.

## Architecture
<img src="architecture.jpg" alt="architecture" width="600">

## How BiasNavi Help Non-Experts for Data Bias Management

| **Challenge**                      | **How BiasNavi Solves It**                       |
|------------------------------------|--------------------------------------------------|
| Lack of technical expertise        | Conversational agent, plain-language guidance    |
| Difficulty understanding bias      | Visualizations with easy-to-understand insights  |
| Inability to configure tools       | Automated detection, prebuilt metrics            |
| No coding knowledge                | Actionable bias mitigation without manual coding |
| Uncertainty about next steps       | Recommendations, simulations, and workflows      |
| Communicating findings             | Automated reporting and visual narratives        |

## Easy Setup
1. Run the following command to set up the project for the first time:
```bash
make setup
# Wait for the docker containers to start the run
make create-db
# To create user and database
```
2. Config your API key and database URL in the file named `config.sample.yaml` under the root directory of the project and rename it to `config.yaml`
3. Start the program.
```bash
make run
```

## Additional Steps
To stop database containers, run:
```bash
make stop-db
```
To stop and delete database containers, run:
```bash
make clean-db
```
To start the database explicitly, run:
```bash
make start-db
```
