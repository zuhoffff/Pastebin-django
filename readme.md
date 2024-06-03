# Design:

## 1. User Interaction:
User can add a block of text through the web GUI or by dropping a text file.

### Features:
- **Text Form**: Implemented.
- **Text File**: Yet to be implemented.
- **Max Size Limit**: To be implemented (10MB).
- **Set Expiry Time**: Users can set the lifespan of their content.
    - **Additional Feature**: Real-time display of time until expiry when viewing the paste.
        - (Todo: Improve timer logic precision, fix timer delay on the main page).
- **Password Protection**: Users can add a password to a block.

### Security:
- Ensure the application is secure.

### User Authentication:
- Users can sign up their text.

## 2. URL Generation:
- User receives a relative URL (using a unique hash generated by the hashing server).

## 3. Metadata Access:
- URLs can be used to access metadata in the database.

## 4. Database:
- Database stores these URLs along with additional metadata.

## 5. Storage:
- Utilizes S3 storage to store the paste (text) itself.
TODO: store s3 credentials in safer way
    - The convention for key to the text paste is combination of its URL and timestamp (and the password if specified).

### Hashing Server:
- Unique URLs generation.
- Implementation of multithreading (Todo).

## Redis:
- Redis stores just the most popular pastes.

### My Cache Design Idea:
- The Redis cache stores key-access pairs as a set.
- If a key is not in the cache:
    - It is pulled from the database, and its access counter increases.
- Flush the cache every N seconds and refill it with the M most popular keys.
- Use two cache pools to use one as buffer.

### Conventional Cahe Design for Read-Heavy applications:
- Use Cache-Aside (along with Read-Through) would be an optimal caching strategy.

### What to Cache:
- Cache all the needed db fields from db (url, author, id, password).
- Cache popular pastes (optional).

## 7. Another feature:
User can navigate to the list of all public pastes

### Other tasks:
- organize the file structure better

#### TODO: create tests.