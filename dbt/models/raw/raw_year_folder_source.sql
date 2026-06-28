{{ config(materialized='view') }}

select *
from {{ source('year_folder_source', 'brazil_net_migration') }}
