*Сеансы: * {{ title }}
*{{ place }}*
*Дата: * {{ date }}
{% for s in seances -%}
{{ s.time }} {% if s.format is not none %} в формате {{ s.format }} {% endif %} от {{ s.minPrice }} руб. {% if s.id > 1 %} /schedule{{ s.id }} {% endif %}
{% endfor %}