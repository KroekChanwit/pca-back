
# import psycopg2
# def connect_db(obj): 

#     try:
#         connect = psycopg2.connect(database=obj['databasename'],
#                             host=obj['ip'],
#                             port=obj['port'],
#                             user=obj['username'],
#                             password=obj['password'])
#         print(f"{obj['databasename']} database Connected")
#     except(Exception, psycopg2.Error) as e:
#         print(f"{obj['databasename']} database Connect Failed: {e}")
    
#     return connect
