# coding: utf-8


def construct_message_with_attachment(recipient_id, attachment_elements,
                                      quick_replies=None):

    if quick_replies:
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": attachment_elements
                    }
                },
                "quick_replies": quick_replies

            }
        }

    else:
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": attachment_elements
                    }
                }
            }
        }

    return payload


def construct_message_with_text(recipient_id, text, quick_replies=None):

    if quick_replies:
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": text,
                "quick_replies": quick_replies
            }
        }
    else:
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": text,
            }
        }

    return payload
