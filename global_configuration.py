# Standard imports
import os

# Pypi imports
import dotenv
import pymongo

#------------------------------------------#
# Global Configuration
#------------------------------------------#

dotenv.load_dotenv()

MONGO_CLIENT = pymongo.MongoClient(os.getenv('MONGODB_URL'))
DATABASE = MONGO_CLIENT.mtglimited