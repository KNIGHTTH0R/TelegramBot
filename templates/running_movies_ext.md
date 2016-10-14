{% if title %} *Кинотеатр: {{ title }}*  {% endif %}
{% if premiers|length > 0 %}
{{ sign_premier }} *Премьеры этой недели:*
{% for prem in premiers -%}
{{ sign_point }} {{ prem.title }} {{ sign_calendar }} {{ prem.link }} {{ sign_newspaper }} {{ prem.link_info }}
{% endfor %}
{% endif %}
{% if videos %} {{ sign_video }} *Фильмы в прокате:* {% endif %}
{% for video in videos -%}
{{ sign_point }} {{ video.title }} {{ sign_calendar }} {{ video.link }} {{ sign_newspaper }} {{ video.link_info}}
{% endfor %}