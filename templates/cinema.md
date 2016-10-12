*Кинотеатры*
{% for s in cinemas -%}
 _{{ s.short_name }}_ {% if s.address %} {{ s.address }}{% endif %} {% if s.mall %} {{ s.mall }} {% endif %} {{ s.link }}
{% endfor %}