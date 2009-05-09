BEGIN TRANSACTION;
CREATE TABLE mapurl(key text primary key, longurl text unique);
COMMIT;
