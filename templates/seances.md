*Кинотеатры*
{% for s in seances %}
 {{ sign_tip }} {{ s.title }} {{ s.link }}
{% endfor %}
