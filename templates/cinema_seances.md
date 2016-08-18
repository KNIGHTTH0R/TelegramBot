*Сеансы: * {{ title }}
{% for s in seances %}
 {{ s.tip }} {{ s.time }} от {{ s.minPrice }}руб. (/schedule{{ s.id }}) \n
{% endfor %}