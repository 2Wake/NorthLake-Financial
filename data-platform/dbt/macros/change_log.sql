{#- raw tables are change logs: a full copy of a record is appended each day it is
    created or changed. These two macros turn a change log into
    (1) the current version of each record, and (2) its full history. -#}

{% macro latest_version(table, key, updated_at='record_updated_at') %}
select *
from {{ source('raw', table) }}
where true
qualify row_number() over (partition by {{ key }} order by {{ updated_at }} desc, _batch_date desc) = 1
{% endmacro %}

{% macro version_history(table, key, updated_at='record_updated_at') %}
select
    *,
    {{ updated_at }} as valid_from,
    lead({{ updated_at }}) over w as valid_to,
    lead({{ updated_at }}) over w is null as is_current
from {{ source('raw', table) }}
window w as (partition by {{ key }} order by {{ updated_at }}, _batch_date)
{% endmacro %}
