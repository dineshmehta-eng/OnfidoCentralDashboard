CREATE OR ALTER VIEW vw_dashboard_consolidated AS
SELECT * FROM dbo.stg_consolidated;
GO

CREATE OR ALTER VIEW vw_slot_wise_performance AS
SELECT * FROM dbo.stg_slot_wise_performance;
GO

CREATE OR ALTER VIEW vw_utilization AS
SELECT * FROM dbo.stg_utilization;
GO

CREATE OR ALTER VIEW vw_audits AS
SELECT * FROM dbo.stg_audits;
GO

CREATE OR ALTER VIEW vw_poa_live AS
SELECT * FROM dbo.stg_poa_live;
GO

CREATE OR ALTER VIEW vw_apr AS
SELECT * FROM dbo.stg_apr;
GO

CREATE OR ALTER VIEW vw_tqbqmq AS
SELECT * FROM dbo.stg_tqbqmq;
GO

CREATE OR ALTER VIEW vw_cre AS
SELECT * FROM dbo.stg_cre;
GO

CREATE OR ALTER VIEW vw_doc_etm AS
SELECT * FROM dbo.stg_doc_etm;
GO

CREATE OR ALTER VIEW vw_doc_task_skip AS
SELECT * FROM dbo.stg_doc_task_skip;
GO

CREATE OR ALTER VIEW vw_poa_etm AS
SELECT * FROM dbo.stg_poa_etm;
GO

CREATE OR ALTER VIEW vw_agent_wise AS
SELECT * FROM dbo.stg_agent_wise;
GO
