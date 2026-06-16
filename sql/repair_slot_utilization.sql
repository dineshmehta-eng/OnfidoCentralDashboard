IF OBJECT_ID('dbo.stg_slot_wise_performance', 'U') IS NULL
BEGIN
    SELECT
        CAST(bst_slot AS NVARCHAR(100)) AS bst_slot,
        CAST(ist_slot AS NVARCHAR(100)) AS ist_slot,
        CAST(tl_s_name AS NVARCHAR(255)) AS tl_s_name,
        CAST(am_s_name AS NVARCHAR(255)) AS am_s_name,
        COUNT(*) AS total_records,
        SUM(TRY_CONVERT(FLOAT, total_time_spent_processing_mins)) AS total_processing_mins,
        SUM(TRY_CONVERT(FLOAT, total_time_spent_inactive_mins)) AS total_inactive_mins,
        SUM(TRY_CONVERT(FLOAT, total_time_spent_unassigned_mins)) AS total_unassigned_mins,
        AVG(TRY_CONVERT(FLOAT, REPLACE(avail, '%', ''))) AS avg_avail_pct,
        COUNT(DISTINCT analyst_email) AS active_analysts,
        MAX(synced_at) AS synced_at
    INTO dbo.stg_slot_wise_performance
    FROM dbo.vw_apr
    GROUP BY bst_slot, ist_slot, tl_s_name, am_s_name;
END

IF OBJECT_ID('dbo.stg_utilization', 'U') IS NULL
BEGIN
    SELECT
        CAST(analyst_email AS NVARCHAR(255)) AS analyst_email,
        CAST(tl_s_name AS NVARCHAR(255)) AS tl_s_name,
        CAST(am_s_name AS NVARCHAR(255)) AS am_s_name,
        SUM(TRY_CONVERT(FLOAT, total_time_spent_processing_mins)) AS processing_mins,
        SUM(TRY_CONVERT(FLOAT, total_time_spent_inactive_mins)) AS inactive_mins,
        SUM(TRY_CONVERT(FLOAT, total_time_spent_unassigned_mins)) AS unassigned_mins,
        SUM(TRY_CONVERT(FLOAT, REPLACE(avail, '%', ''))) AS avail_pct_total,
        AVG(TRY_CONVERT(FLOAT, REPLACE(avail, '%', ''))) AS avg_avail_pct,
        COUNT(*) AS total_records,
        MAX(synced_at) AS synced_at
    INTO dbo.stg_utilization
    FROM dbo.vw_apr
    GROUP BY analyst_email, tl_s_name, am_s_name;
END

IF OBJECT_ID('dbo.vw_slot_wise_performance', 'V') IS NULL
    EXEC('CREATE VIEW dbo.vw_slot_wise_performance AS SELECT * FROM dbo.stg_slot_wise_performance');

IF OBJECT_ID('dbo.vw_utilization', 'V') IS NULL
    EXEC('CREATE VIEW dbo.vw_utilization AS SELECT * FROM dbo.stg_utilization');
