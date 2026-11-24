{#- Use the dataset named in +schema exactly (staging, marts), instead of dbt's
    default "<target>_<schema>" naming, which would create new datasets. -#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name if custom_schema_name else target.schema }}
{%- endmacro %}
