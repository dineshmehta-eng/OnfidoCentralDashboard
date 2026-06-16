/*
Give this script to your SQL Server DBA (or anyone with sysadmin role).
Run this first, then run python sql/setup_database.py to deploy views/indexes inside the DB.
*/

-- 1. Create the database (only if it doesn't exist)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'Onfido_DB')
    CREATE DATABASE Onfido_DB;
GO

-- 2. Add the Windows user as db_owner inside Onfido_DB (adjust login name if your domain is different)
USE Onfido_DB;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'MAS-NOIDA\Dineshm')
    CREATE USER [MAS-NOIDA\Dineshm] FOR LOGIN [MAS-NOIDA\Dineshm];
GO

ALTER ROLE db_owner ADD MEMBER [MAS-NOIDA\Dineshm];
GO

-- (Optional) Enable sa login with a strong password if you prefer SQL auth over Windows Auth
-- ALTER LOGIN sa ENABLE;
-- ALTER LOGIN sa WITH PASSWORD = 'YOUR_STRONG_PASSWORD_HERE', CHECK_POLICY = ON;
GO

PRINT 'Onfido_DB created and MAS-NOIDA\Dineshm granted db_owner.';
