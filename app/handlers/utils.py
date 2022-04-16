from aiogram.utils.emoji import emojize
import aiogram.utils.markdown as fmt


def get_product_text_message(product: dict) -> str:
    name = product.get("name")
    price = product.get("price")
    shop = product.get("shop")
    url = product.get("url")
    print(url)
    return emojize(fmt.hlink(fmt.text(
        fmt.text(":arrow_right:", name),
        fmt.text(":exclamation:", "price:", fmt.text(price)),
        fmt.text(":shopping_cart:", "shop:", fmt.text(shop)),
        sep="\n"), url)
    )
