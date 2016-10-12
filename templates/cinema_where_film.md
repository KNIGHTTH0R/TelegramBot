{% if film_name %} *Фильм: "{{ film_name }}"* {% endif %}
{% for s in seances -%}
 _{{ s.short_name }}_ {% if s.address %} {{ s.address }}{% endif %} {% if s.mall %} {{ s.mall }} {% endif %} {{ s.link }}
{% endfor %}