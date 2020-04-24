#
# Sets up the database for the website.
#

from . import db, create_app



print("============================")
print("  Creating the Database...  ")
print("============================")
print(" ")

# Create the database.
db.create_all(app=create_app())

print(" ")
print("Created the database.")
print(" ")
