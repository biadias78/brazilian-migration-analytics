{{ config(materialized='view') }}

with source_data as (
    select *
    from {{ ref('raw_year_folder_source') }}
)

select
    country,
    coub,
    fborn,
    edu_lfs,
    edu_cen,
    age_lfs,
    age_cen,
    nat,
    number,
    reg_oecd,
    reg_regions,
    sex,
    dos_lfs,
    dos_cen,
    lfs_lfs,
    occupation,
    sector,
    field_edu,
    national,
    nationality,
    age,
    edu_detailed,
    birth,
    oecd,
    oecdb,
    source,
    regionb,
    recent,
    lfs,
    occ_08,
    occ_1d,
    occ_other,
    occ_88,
    skill_occ,
    overqualified
from source_data
where number is not null
