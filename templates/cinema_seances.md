*Сеансы: * {{ title }}
*{{ place }}*
*Дата: * {{ date }}
{% for s in seances -%}
{{ s.time }} от {{ s.minPrice }} руб. {% if s.id > 1 %} /schedule{{ s.id }} {% endif %}
{% endfor %}