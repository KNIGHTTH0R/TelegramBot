{% if title %} *Кинотеатр: {{ title }}*  {% endif %}
{% if premiers|length > 0 %}
{{ sign_premier }} *Премьеры этой недели:*
{% for prem in premiers -%}
{{ sign_point }} {{ prem.title }} {{ prem.link }}
{% endfor %}
{% endif %}
{% if videos %} {{ sign_video }} *Фильмы в прокате:* {% endif %}
{% for video in videos -%}
{{ sign_point }} {{ video.title }} {{ video.link }}
{% endfor %}
