def currency_context(request):
    currency_symbol = '$' # Default
    if request.user.is_authenticated:
        # Assuming we added a property or we can fetch the choice display
        # Let's use the property we added to the model
        currency_symbol = request.user.currency_symbol
    return {'currency_symbol': currency_symbol}
