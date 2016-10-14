*Кинотеатры*
{% for s in seances -%}
{{ sign_point }} {{ s.title }} {{ s.distance }} м. {{ s.link }}
{% endfor %}


