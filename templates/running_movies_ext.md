{{ sign_video }} Фильмы в прокате:
{% for video in videos -%}
 {{ video.title }} {{ sign_calendar }} {{ video.link }} {{ sign_newspaper }} {{ video.link_info}}
{% endfor %}
{% if premiers|length > 0 %}
{{ sign_premier }} Премьеры этой недели:
{% for prem in premiers -%}
{{ prem.title }} {{ sign_calendar }} {{ prem.link }} {{ sign_newspaper }} {{ prem.link_info }}
{% endfor %}
{% endif %}