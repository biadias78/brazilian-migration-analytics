{{ config(materialized='table') }}

with staged as (
    select *
    from {{ ref('stg_year_folder') }}
where lower(coub) like '%bra%' or lower(coub) like '%brazil%'
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
from staged
