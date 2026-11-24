{#- Fails rows where the expression is false (rows where it is NULL are ignored). -#}
{% test expression_is_true(model, expression) %}
select *
from {{ model }}
where not ({{ expression }})
{% endtest %}
