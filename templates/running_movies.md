{% if title %} *Кинотеатр: {{ title }}*  {% endif %}
{{ sign_video }} Фильмы в прокате:
{% for video in videos -%}
 {{ video.title }} {{ video.link }}
{% endfor %}
{% if premiers|length > 0 %}
{{ sign_premier }} Премьеры этой недели:
{% for prem in premiers -%}
{{ prem.title }} {{ prem.link }}
{% endfor %}
{% endif %}