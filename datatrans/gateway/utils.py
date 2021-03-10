def text_or_else(element, else_value='') -> str:
    if element is not None:
        return element.text
    else:
        return else_value
