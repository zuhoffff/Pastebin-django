# Design:

## 1. User Interaction:
User can add a block of text through the web GUI.
TODO: implement file input

### Features:
- **Text Form**: Implemented.
- **Text File**: Yet to be implemented.
- **Max Size Limit**: To be implemented (10MB).
- **Set Expiry Time**: Users can set the lifespan of his text.
    - **Additional Feature**: Real-time display of time until expiry when viewing the paste.
- **Password Protection**: Users can add a password to a block.

### User Authentication:
- Users can sign up his text.

## 2. URL Generation:
- User receives a relative URL (using a unique hash generated by the hashing server).

## 3. Metadata Access:
- URLs can be used to access metadata in the database.

## 4. Database:
- Database stores these URLs along with additional metadata.

## 5. Storage:
- Utilizes S3 storage to store the paste (text) itself.
    - The example convention for key to the text paste: just URL slug

## 6. Hashing Server:
- Unique URLs (slug) generation.
- Multithread access.
Design:
1. check for the amount of spare hashes every N time
1. restore number of spare hashes everytime server is free of requests (if they arrive continuously, handle cases when get_hash has no hash to return).

## 7. Redis:
- Redis caching added.

### Conventional Cahe Design for Read-Heavy applications:
- Using Cache-Aside (along with Read-Through) would be an optimal caching strategy.

### What to Cache:
- Cache all the needed db fields from db (url, author, id, password).
- Cache popular pastes (optional).

## 7. Another feature:
 User can navigate to the list of all pastes.

#### TODO: create more tests.