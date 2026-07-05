{{ config(materialized='view') }}

with brazil_outflow as (
    select *
    from {{ ref('stg_migration_stock') }}
)

select
    destination,
    year,
    sum(total) as total_migrants,
    sum(male) as total_male,
    sum(female) as total_female,
    case when sum(total) is null or sum(total) = 0 then null else sum(male) / sum(total) end as male_ratio,
    case when sum(total) is null or sum(total) = 0 then null else sum(female) / sum(total) end as female_ratio
from brazil_outflow
where lower(cast(origin as varchar)) like '%brazil%'
  and destination is not null
group by destination, year
order by year, total_migrants desc
