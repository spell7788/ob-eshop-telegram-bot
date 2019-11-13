import json
from typing import Any, Dict

from aiogram import types
from aiogram.dispatcher import FSMContext

from ..bot import settings  # type: ignore
from ..product_answers import get_product
from ..product_filters import ProductFilters
from ..utils import is_admin


async def prepare_order_data(
    state: FSMContext, pre_checkout_query: types.PreCheckoutQuery
) -> Dict[str, Any]:
    payload = json.loads(pre_checkout_query.invoice_payload)
    product_index, product_filters, size_id = payload
    product = await get_product(state, product_index, ProductFilters(product_filters))
    order_info, address = (
        pre_checkout_query.order_info,
        pre_checkout_query.order_info.shipping_address,
    )
    return {
        "items": [{"shoes": product.id, "quantity": 1, "size": int(size_id)}],
        "full_name": order_info.name,
        "mobile_number": order_info.phone_number,
        "shipping_type": pre_checkout_query.shipping_option_id,
        "shipping_city": f"{address.state} {address.city}",
        "shipping_department": (
            f"{address.street_line1} {address.street_line2} {address.post_code}"
        ),
        "paytype": "online_payment",
        "status": "awaiting_fulfillment",
        "debug": settings.DEBUG or is_admin(pre_checkout_query.from_user.id),
    }
