export const getValueFromOfferOrProduct = (key, offer, product) => {
  if (!offer) {
    return
  }

  const isCreatedEntity = !offer.id
  if (isCreatedEntity) {
    return product[key]
  }

  return offer[key]
}
