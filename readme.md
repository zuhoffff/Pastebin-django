# design:

## 1.User can add a block of text thru web gui or drop a txt file there:
- text form - implemented
- tetxt file - TODO:\
features:
1. max size is 10mb,
1. user can set time of life of this content
1. user can add password to a block

## 2.User get in return a relative URL (which includes the hash generated based on id of metadata)
## 3.Such url points to the metadata in the db
## 4.Metadata can be used as a key to s3 storage
## Hashing server: 
1. firtly hash-server will its db with seeds for future hashes\
1. make urls unique -> make hashing server for this purpose\
1. and implement CASHING for hashes (redis)\
1. also implement multithreading to it\
## redis:
redis will store just popular and keys (so popular text can be accessed fast)
##### cahce design: 
* the redis cache stores key-accesses pair as a set
* if key its not on the cash:
*    it is pulled from the db and its accesses gets increased
*  flush the cache every N seconds and refill it with M most popular keys