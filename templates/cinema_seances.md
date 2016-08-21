*Сеансы: * {{ title }}
{% for s in seances %}
 {{ s.tip }} {{ s.time }} от {{ s.minPrice }}руб. {% if s.id > 1 %} (/schedule{{ s.id }}) {% endif %}
{% endfor %}