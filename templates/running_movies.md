{{ sign_video }} Фильмы в прокате:
{% for video in videos -%}
 {{ video.title }} /info{{ video.link }}
{% endfor %}
{% if premiers|length > 0 %}
{{ sign_premier }} Премьеры этой недели:
{% for prem in premiers -%}
{{ prem.title }} /info{{ prem.link }}
{% endfor %}
{% endif %}