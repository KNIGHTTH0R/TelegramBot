*Сеансы: * {{ title }}
*{{ place }}*
*Дата: * {{ date }}
{% for s in seances -%}
{{ s.time }} {% if s.format is not none %} в формате {{ s.format }} {% endif %} {% if s.minPrice %} от {{ s.minPrice }} руб. {% endif %} {% if s.id > 1 %} /schedule{{ s.id }} {% endif %}
{% endfor %}