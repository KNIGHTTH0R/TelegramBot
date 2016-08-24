*Кинотеатры*
{% for s in seances -%}
{{ s.title }} {{ s.distance }} м. {{ s.link }}
{% endfor %}


