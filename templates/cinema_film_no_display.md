{% for c in cinemas %}
Кинотеатр *{{ c.title }}* не показывает:
    {% for f in c.films %}
    {{ sign_point }} _{{ f.title }}_ /info{{ f.link }} 
    {% endfor %}
{% endfor %}