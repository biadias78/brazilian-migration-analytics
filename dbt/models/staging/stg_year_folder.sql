{{ config(materialized='view') }}

with source_data as (
    select *
    from {{ ref('raw_year_folder_source') }}
)

select
    country as destination_country,
    coub as origin_country_code,
    fborn as birth_country_code,
    edu_lfs as education_level,
    edu_cen as education_detail,
    age_lfs as age_group,
    age_cen as age_detail,
    nat as nationality_code,
    number as total_migrants,
    reg_oecd as oecd_region,
    reg_regions as region,
    sex,
    dos_lfs as demo_lfs,
    dos_cen as demo_cen,
    lfs_lfs as labor_force_status,
    occupation,
    sector,
    field_edu as field_of_education,
    national as national_flag,
    nationality,
    age,
    edu_detailed as education_detailed,
    birth as birth_place,
    oecd as oecd_indicator,
    oecdb as oecd_secondary,
    source,
    regionb as region_b,
    recent as recent_migrant,
    lfs as lfs_code,
    occ_08,
    occ_1d,
    occ_other,
    occ_88,
    skill_occ as skill_occupation,
    overqualified
from source_data
where number is not null
