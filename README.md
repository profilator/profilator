# profilator
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/profilator/profilator.svg?branch=master)](https://travis-ci.org/profilator/profilator)

Flask application for generating user's Twitter profile report.

## Installation

First, clone this repository to your local computer:
```
git clone https://github.com/profilator/profilator.git
cd profilator
```

Then install the necessary packages with pip:
```
pip3 install -r requirements.txt 
```

You may want to use virtualenv to avoid installing dependencies system-wide, like this:
```
python -m venv ENV
source ENV/bin/activate
pip3 install -r requirements.txt
```

Next, head to the source folder, and start the dev server on ```localhost:5000```:
```
cd source
python app.py
```
