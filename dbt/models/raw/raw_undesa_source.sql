{{ config(materialized='view') }}

select *
from {{ source('undesa_source', 'undesa_migration') }}