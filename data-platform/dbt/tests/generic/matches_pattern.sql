{#- Fails rows where a non-empty value doesn't fully match a regular expression. -#}
{% test matches_pattern(model, column_name, pattern) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and not regexp_contains({{ column_name }}, r'{{ pattern }}')
{% endtest %}
