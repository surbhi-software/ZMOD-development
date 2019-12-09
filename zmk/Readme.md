# Zementis Modeler (ZMOD)

<img src="https://github.com/SoftwareAG/ZMOD/blob/master/docs/zmod_logo.png" alt="zmod_logo" height="120" style="float:right"/>

**Zementis modeler** is an open source machine learning and artificial intelligence platform for Data Scientist to solve business problems faster and quicker, build prototypes and convert them to actual project. The modeler helps from data preparation to model building and deployment, the tool supports large variety of algorithms that can be run without a single line of code. The web based tool has various components which help Data Scientist to perfrom several model building tasks and provides deployment ready PMML files which can be hosted as a REST services.

Zementis Modeler allows its user to cover wide variety of algorithms and Deep Neural Network architectures, with minimal or No code enviornment. It is also one of the few deep-learning platforms to support the Predictive Model Markup Languaue (PMML) format, PMML allows for different statistical and data mining tools to speak the same language. The feature offerings of Zementis Modeler are:
* **Zementis AutoML** : Automatically train Machine learning models on data supports huge space of algorithms and hyper parameters tuning.
* **Zementis Model Editor** : Create Deep Neural Network models using drag and drop functionality, which supports wide variety of model layers, once model architecture is ready, train your model. Zementis Modeler Editor also comes with pre-trained architcture templates that helps in quick model building and training.
* **Jupyter Notebook** : Zementis Modeler comes with integrated Jupyter Notebook (For R and Python).
* **Tensorboard** : Zementis Modeler provides Tensorboard dashboard to show the progress of models.
* **Code Execution** : Zementis Modeler provides support of executing Python script files for more advance requirements.
* **REST API Support** : Zementis Modeler can be used using REST calls and can be used as a deployment tool.

**Zementis Modeler** comes to you with the complete source code in Python, .Net, Angular, docker files and extended HTML documentation on how to use guidelines, and a growing number of video, blogs and tutorials that help you familiarize yourself with the way Zementis Modeler supports a Data Scientist on becoming more productive.

# ZMK

ZMK is the Django REST based application which handles all the AI/ML related training, scoring, deployment tasks.

**Components of ZMK**:

1. **NyokaBase**: Nyoka to convert the models in PMML and then reconstruct to retrain or deployment
2. **NyokaServer**: This is the individual app within Django framework to support drag and drop functionality in UI and write PMML based on the user actions
3. **Scoring**: This is the individual app within Django framework to score deployed model on test data or new data
4. **trainModel**: This is the individual app within Django framework to train AutoML and NN models
5. **Utility**: This is the individual app within Django framework to support additional functionalities like download a file, code utilities like execute a Python file.

**To start the ZMK app**: `python manage.py runserver` and other django parameters are supported by default

**To access the ZMK swagger**: `localhost:{port}/` default `localhost:8888/`



# Quick Demo of Zementis Modeler :

[Demo 1 : Distracted Driver Use Case](https://www.zmod.org/learn/0SZHvRSJwyc)<br/>
[Demo 2 : AutoML](https://www.zmod.org/learn/6RUJ0Nk52u8)<br/>
[Demo 3 : Import data from Cumulocity](https://www.zmod.org/learn/_YCGPhMETF4)<br/>
[Demo 4 : Jupyter Notebook](https://www.zmod.org/learn/dm98Rjb8l6w)<br/>
[Demo 5 : Python Execution](https://www.zmod.org/learn/Hnu7lvcc0kc)<br/>