from .bot import N_  # type: ignore

START = N_(
    """\
Welcome $first_name, I $bot_mention will help you pick up and buy wonderful shoes.
To continue, use the keyboard below or commands described in /help."""
)


HELP = N_(
    """\
When communicating with the bot, your primary command will be /browse or /b - which \
allows you to pick and operate, including purchasing, some shoes. \
Type /contacts to be able to contact us, /help to display this message. \
Note that each of the above commands has a keyboard counterpart."""
)

CONTACTS = N_(
    """\
You can contact us in any of the following ways:
:telephone_receiver: Phone
$phones

:e-mail: Email
$emails"""
)

INVOICE_DESCRIPTION = N_(
    """\
I see, you have chosen this model.
A very good choice.
I believe you will like it. :wink: :thumbs_up:"""
)

ORDER_NOTIFICATION = N_(
    """\
*Order* created _${datetime_now}_ on sum _$total_amount ${currency}_

[$product_name $product_code]($product_url) of size *$size*

```
Customer name: $name
Phone number: $phone_number
Country code: $country_code
State: $state
City: $city
Street 1: $street_line1
Street 2: $street_line2
Post code: $post_code
```"""
)
