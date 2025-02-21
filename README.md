# 4353GP
## Group Name - Toronto


# Project Overview
The first iteration of the group project aims to provide you with hands-on experience in building a web-based user management system that leverages Office365 for authentication.

# Setup and running locally
After creating your virtual envirmoment, you can install the dependicies using
```bash
pip3 install -r requirements.txt
```
You then have to create a local PostgreSQL database. Install PostgreSQL and ensure it runs smoothly.
Create a .env file to setup your environment variables. It should include

```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
DATABASE_URL=your_database_url
```

Create your local database and local user.
For local testing I recommend creating user `flaskuser` with `flaskpass` and `flaskdb`
`DATABASE_URL` follows the following path `postgresql://<username>:<password>@<host>/<database_name>`

After creating the database with the credentials, run:

```bash
flask db init
flask db migrate -m "Initial migrate"
flask db upgrade
```
This should automatically create a table in your local database. If any errors happen, godspeed youre on your own.

To run it locally first activate the virtualenv
Then in your console type:
```bash
flask --app wsgi:app run
```
or
```bash
python3 run.py
```


# Config
Default and global config is located under `root/config.py`.

