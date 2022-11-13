# Following file is for the database integration which uses postgres SQL Repository

import psycopg2
import psycopg2.extras
import logging 

# Enabling Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


# Initialising database login credentials
DB_HOST = "SAMPLE"
DB_NAME = "SAMPLE"
DB_USER = "SAMPLE"
DB_PASS = "SAMPLE"

def execute_query(query):
    
    # Connecting with the database
    #logger.info("connecting with database & executing the query")

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        try:
            # Executing the query
            cur.execute(query)

        except Exception as exp:
            logger.info("error occured in database query")
            logging.error(exp)
        
        try:
            data = cur.fetchall()
            logger.info("data fetched from database")
            
        except psycopg2.ProgrammingError:
            # when no result to be fetched like the insert query
            data = None
            logger.info("data added/updated on database")

        except Exception as exp:
            pass
        
    conn.commit()
    conn.close()
    
    return data
