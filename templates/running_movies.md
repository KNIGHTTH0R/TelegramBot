{{ sign_video }} Фильмы в прокате:
{% for video in videos %}
 {{ sign_tip }} {{ video.title }} (/info{{ video.link }})
{% endfor %}
{{ sign_premier }} Премьеры этой недели:
{% for prem in premiers %}
 {{ sign_tip }} {{ prem.title }} (/info{{ prem.link }})
{% endfor %}