-- Indexes for staging tables (only indexable columns: id + synced_at)
-- Most columns are nvarchar(max); SQL Server can't use them as index keys.

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_consolidated_synced_at' AND object_id = OBJECT_ID('dbo.stg_consolidated'))
    CREATE NONCLUSTERED INDEX IX_stg_consolidated_synced_at ON dbo.stg_consolidated(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_audits_synced_at' AND object_id = OBJECT_ID('dbo.stg_audits'))
    CREATE NONCLUSTERED INDEX IX_stg_audits_synced_at ON dbo.stg_audits(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_poa_live_synced_at' AND object_id = OBJECT_ID('dbo.stg_poa_live'))
    CREATE NONCLUSTERED INDEX IX_stg_poa_live_synced_at ON dbo.stg_poa_live(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_apr_synced_at' AND object_id = OBJECT_ID('dbo.stg_apr'))
    CREATE NONCLUSTERED INDEX IX_stg_apr_synced_at ON dbo.stg_apr(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_tqbqmq_synced_at' AND object_id = OBJECT_ID('dbo.stg_tqbqmq'))
    CREATE NONCLUSTERED INDEX IX_stg_tqbqmq_synced_at ON dbo.stg_tqbqmq(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_cre_synced_at' AND object_id = OBJECT_ID('dbo.stg_cre'))
    CREATE NONCLUSTERED INDEX IX_stg_cre_synced_at ON dbo.stg_cre(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_doc_etm_synced_at' AND object_id = OBJECT_ID('dbo.stg_doc_etm'))
    CREATE NONCLUSTERED INDEX IX_stg_doc_etm_synced_at ON dbo.stg_doc_etm(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_doc_task_skip_synced_at' AND object_id = OBJECT_ID('dbo.stg_doc_task_skip'))
    CREATE NONCLUSTERED INDEX IX_stg_doc_task_skip_synced_at ON dbo.stg_doc_task_skip(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_poa_etm_synced_at' AND object_id = OBJECT_ID('dbo.stg_poa_etm'))
    CREATE NONCLUSTERED INDEX IX_stg_poa_etm_synced_at ON dbo.stg_poa_etm(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_stg_agent_wise_synced_at' AND object_id = OBJECT_ID('dbo.stg_agent_wise'))
    CREATE NONCLUSTERED INDEX IX_stg_agent_wise_synced_at ON dbo.stg_agent_wise(synced_at);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_etl_sync_log_synced_at' AND object_id = OBJECT_ID('dbo.etl_sync_log'))
    CREATE NONCLUSTERED INDEX IX_etl_sync_log_synced_at ON dbo.etl_sync_log(synced_at);
GO
