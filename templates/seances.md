*Кинотеатры*
{% for s in seances -%}
{{ s.title }} {{ s.link }}
{% endfor %}