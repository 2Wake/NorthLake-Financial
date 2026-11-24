{#- Privacy check: fails rows whose free text contains a phone number or email address. -#}
{% test no_contact_details_in_text(model, column_name) %}
select {{ column_name }}
from {{ model }}
where regexp_contains({{ column_name }}, r'\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|[\w.+-]+@[\w-]+\.[\w.]+')
{% endtest %}
