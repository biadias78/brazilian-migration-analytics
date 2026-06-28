{{ config(materialized='view') }}

with source_data as (
    select *
     from {{ ref('raw_undesa_source') }}
)

select
    destination,
    origin,
    coverage,
    data_type,
    destination_code,
    origin_code,
    cast(year as integer) as year,
    cast(total as double) as total,
    cast(male as double) as male,
    cast(female as double) as female
from source_data
where destination is not null
  and origin is not null