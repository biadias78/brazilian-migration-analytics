{{ config(materialized='table') }}

with staged as (
    select *
    from {{ ref('stg_migration_stock') }}
    where lower(origin) like '%brazil%' or lower(origin_code) = 'bra'
)

select
    destination,
    origin,
    destination_code,
    origin_code,
    coverage,
    data_type,
    year,
    total,
    male,
    female,
    case when total is null or total = 0 then null else male / total end as male_ratio,
    case when total is null or total = 0 then null else female / total end as female_ratio,
    case when total is null or total = 0 then null else male - female end as sex_difference,
    case when total is null or total = 0 then null else (male - female) / total end as sex_difference_ratio
from staged
