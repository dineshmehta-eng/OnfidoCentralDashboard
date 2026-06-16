-- Optional helper stored procedures

CREATE OR ALTER PROCEDURE usp_refresh_views
AS
BEGIN
    SET NOCOUNT ON;
    PRINT 'Standard views do not require refresh.';
END;
GO

CREATE OR ALTER PROCEDURE usp_etl_log_insert
    @spreadsheet_url NVARCHAR(500) = NULL,
    @sheet_name NVARCHAR(128) = NULL,
    @table_name NVARCHAR(128),
    @rows_read INT = 0,
    @rows_inserted INT = 0,
    @sync_status NVARCHAR(50) = 'success',
    @error_message NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO etl_sync_log (spreadsheet_url, sheet_name, table_name, rows_read, rows_inserted, sync_status, error_message, synced_at)
    VALUES (@spreadsheet_url, @sheet_name, @table_name, @rows_read, @rows_inserted, @sync_status, @error_message, GETDATE());
END;
GO
