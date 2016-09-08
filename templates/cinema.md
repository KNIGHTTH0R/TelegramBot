*Кинотеатры*
{% for s in cinemas -%}
_{{ s.title }}_ {{ s.link }}
{% endfor %}