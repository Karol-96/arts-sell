To test the file and authentication flow:
1. Set up environment, install required package from requirements.txt
```python
pip install -r requirements.txt
```
2. Initialize mysql server, create a database name 'artspace' and simply copy the CREATE TABLE users in the database.sql
3. Update the mysql configurations in __init__.py, set the host, user and password to your setting
4. Run python run.py
5. Register for an account first before you can log in
6. Currently, there's no explicit privileges for admin and artist yet as it depends on the other features.