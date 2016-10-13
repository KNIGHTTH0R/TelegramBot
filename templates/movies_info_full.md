*{{ title }}* 
{{ description.title }} {{ description.link }}
{% if premier %} {{ sign_calendar }} в России {{ premier }} {% endif %}
{% if age %} {{ kinder }} {{ age }} {% endif %}
{% if duration %} {{ sign_time }} {{ duration }} мин. {% endif %}
{% if genres %} {{ sign_genre }} {{ genres }} {%- endif %}
{% if actors %} {{ sign_actor }} {{ actors }} {%- endif %}
{% if directors %}{{ sign_producer }} {{ directors }} {%- endif %}