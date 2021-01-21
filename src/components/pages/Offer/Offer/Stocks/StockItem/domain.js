export const validateCreatedStock = stock => {
  let errors = {}

  if (stock.price < 0) {
    errors.price = 'Le prix doit être positif.'
  }

  if (stock.quantity < 0) {
    errors.quantity = 'La quantité doit être positive.'
  }

  return errors
}

export const validateUpdatedStock = stock => {
  let errors = validateCreatedStock(stock)

  const remainingQuantity = stock.quantity - stock.bookingsQuantity

  if (stock.quantity !== '' && remainingQuantity < 0) {
    const missingQuantityMessage = 'La quantité ne peut être inférieure au nombre de réservations.'
    if ('quantity' in Object.keys(errors)) {
      errors.quantity = errors.quantity.concat('\n', missingQuantityMessage)
    } else {
      errors.quantity = missingQuantityMessage
    }
  }

  return errors
}
