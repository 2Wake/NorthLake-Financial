{#- Fails (or warns) when a data-quality rule has any failing records in fct_dq_findings. -#}
{% test rule_has_no_findings(model, rule_id) %}
select * from {{ model }} where rule_id = '{{ rule_id }}'
{% endtest %}
