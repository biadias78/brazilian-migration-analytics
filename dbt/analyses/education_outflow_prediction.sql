with education_outflow as (
    select
        year,
        education_group,
        total_migrants,
        lag(total_migrants) over (partition by education_group order by year) as previous_year_total,
        case
            when lag(total_migrants) over (partition by education_group order by year) is null then null
            else total_migrants - lag(total_migrants) over (partition by education_group order by year)
        end as year_delta
    from {{ ref('dim_brazil_education_features') }}
)

select
    year,
    education_group,
    total_migrants,
    previous_year_total,
    year_delta,
    case
        when previous_year_total is null then null
        else year_delta / previous_year_total
    end as growth_rate,
    case
        when education_group = 'high education' then 1
        else 0
    end as high_education_flag
from education_outflow
order by year desc, growth_rate desc
