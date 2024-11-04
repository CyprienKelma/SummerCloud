# Summer Cloud

Summer Cloud is a Django web application that allows users to store files on the server. The files are stored in the server's file system. The application provides a web interface to manage files and folders.

## Team
- Nathan Eudeline
- Cyprien Kelma
- Paul Pousset
- Nolan Cacheux


## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
npm install
npm run build
```

## Usage

```bash
source venv/bin/activate
python3 manage.py runserver
```

or

```bash
docker-compose up
```

**Demo user :**

> *.sqlite3 file is provided with a demo user*

> *the media folder is provided with some files*
```txt
username: bafbi
password: TyTbfc%G#lCZL4
```

**Development :**
```bash
source venv/bin/activate
python3 manage.py runserver
npm run watch
```

## Project

**Ouvert le :** jeudi 17 octobre 2024, 12:00

**À rendre :** vendredi 8 novembre 2024, 23:59

### Description

Develop a Cloud Drive application (similar to Google Drive and OneDrive) using Django. To make the project simpler, the files will be stored on the server. The base folder of each user will be his login.

The tool can also work on local storage in replacement of File Explorer.

For example, if there are two users "foo" and "bar" that have uploaded some files, the file structure on the server will be simialr to this one:


- ***base\_server\_folder/*** (root)
  - *foo/* (user1)
    - **file1.txt**
    - *images/*
      - **eiffel tower.png**
  - *bar/* (user2)
    - **bread recipe.pdf**
    - *2024/*
    - **python lecture.pfg**

### Features

The web application will provide the maximum of the following features:

[x] Authentication and account creation with login and password

[x] Browse files and folders on a web UI

[ ] Display file properties and file metadata

[x] Upload files

[x] Create folders

[ ] Move and copy files and folders

[ ] Each account has a drive limit of 100 MB (his folder on the server cannot exceed 100 MB)

[x] The max upload size is 40 MB (a file greater than 40MB cannot be uploaded)

[ ] The web app provides an account info screen that shows statics using graphics

[ ] Example of graphic : space distribution per format (images, documents, videos, ...)

[ ] Preview the maximum of known formats (images, videos, pdf, source code, documents, ...)

[x] Setup script to install requirements and demo data in sqlite.

[x] (3+ person group) Nice, beautiful, responsive UX (demo on laptop and smartphone)

[ ] (4 person group) Open text, view images, play videos

### Deliverable

- A single zip file containing your source code, and at least Readme.md file explaining how the evaluator can run the project in his local computer if the setup script is not available.


### Some example screens

![](https://junia-learning.com/pluginfile.php/114707/mod_assign/intro/image%20%282%29.png)

![](https://junia-learning.com/pluginfile.php/114707/mod_assign/intro/image%20%281%29.png)

![](https://junia-learning.com/pluginfile.php/114707/mod_assign/intro/image.png)
