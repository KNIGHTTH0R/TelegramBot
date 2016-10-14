*Кинотеатры* {% if date %} *{{ date }}* {% endif %}
{% for s in seances -%}
{{ sign_point }} _{{ s.short_name }}_ {% if s.address %} {{ s.address }}{% endif %} {% if s.mall %} {{ s.mall }} {% endif %} {{ s.link }}
{% endfor %}