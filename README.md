# {Music Storyteller}

{Music Storyteller is a project that takes an input from the user a song and tells it as a story.}

## Requirements
- Python {version} or later

### How to install python using MiniConda
1) Download and install Miniconda [here](https://www.anaconda.com/docs/getting-started/miniconda/install)
2) create a new environment using this command:
```bash
$ conda create -n {envname} python={version}
```
3) activate environment using this command:
```bash
$ conda activate {envname}
```
### (Optional) Setup command line interface for better readability
```bash
$ export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```
## Installation

### Install required packages
```bash
$ pip install -r requirements.txt
```

### Setup Environment Variables
```bash
$ cp .env.example .env
```
Set your environment variables in the `.env` file. Like the `OPENAI_API_KEY` value.

## Run the FastAPI Server
```bash
$ uvicorn main:app --reload --port 7000
```
