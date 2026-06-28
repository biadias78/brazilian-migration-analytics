{{ config(materialized='view') }}

with brazil_outflow as (
    select *
    from {{ ref('stg_migration_stock') }}
    where lower(origin) like '%brazil%' or lower(origin_code) = 'bra'
)

select
    coalesce(data_type, 'unknown') as education_group,
    year,
    sum(total) as total_migrants,
    sum(male) as total_male,
    sum(female) as total_female,
    count(*) as row_count,
    case when sum(total) is null or sum(total) = 0 then null else sum(male) / sum(total) end as male_ratio,
    case when sum(total) is null or sum(total) = 0 then null else sum(female) / sum(total) end as female_ratio
from brazil_outflow
group by coalesce(data_type, 'unknown'), year
order by year, total_migrants desc
