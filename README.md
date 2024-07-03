# BulletinExplorer_v2
This project is designed for NTUST students, providing Telegram users with the ability to subscribe to topics. It uses web scraping to gather information from various university websites.

## Table of Contents
- [Packages and Tools](#Packages-and-Tools)
- [Install](#Install)
    - [Clone the repository](#Clone-the-repository)
    - [Navigate to the cloned directory](#Navigate-to-the-cloned-directory)
    - [Run setup script](#Run-setup-script)
- [Usage](#Usage)
    - [build postgres docker](#build-postgres-docker)
    - [run main function](#run-main-function)
- [Debug](#Debug)

## Packages and Tools
* git
* python==3.8.10
* docker==26.1.4

## Install 
### 1. Clone the repository
    $ https://github.com/hhjjy/BulletinExplorer_v2.git
(You must have Git installed, you can install it via `sudo apt update && sudo apt install git` if not already installed.)
### 2. Navigate to the cloned directory
    $ cd BulletinExplorer_v2
### 3. Run setup script
    $ pip install -r requirements.txt

## Usage
### 1. build postgres docker
    $ ./run.sh  
### 2. run main function
    $ python3 main.py
    
## Debug
### 1. build postgres docker
* To get into docker container.
    ```bash
    docker exec -it postgres-main bash
    ```

* Run mydb_schema.sql
    ```bash
    psql -U admin -d mydb -f /docker-entrypoint-initdb.d/mydb_schema.sql
    ```

* Get into psql, and use `12345` to log in.
    ```bash
    psql -h 127.0.0.1 -p 5432 -U admin -d mydb
    ```

* Show all tables `\dt`.
