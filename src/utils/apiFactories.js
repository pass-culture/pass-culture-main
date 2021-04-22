export const offerFactory = (
  customOffer = {},
  customStock = stockFactory(),
  customVenue = venueFactory()
) => {
  const stocks = customStock === null ? [] : [customStock]

  return {
    id: 'O1',
    isEvent: false,
    status: 'ACTIVE',
    stocks,
    venue: customVenue,
    ...customOffer,
  }
}

export const venueFactory = (customVenue = {}, customOfferer = offererFactory()) => {
  return {
    id: 'V1',
    managingOfferer: customOfferer,
    managingOffererId: customOfferer.id,
    name: 'Le nom du lieu',
    ...customVenue,
  }
}

export const offererFactory = (customOfferer = {}) => {
  return {
    id: 'OR1',
    name: 'La nom de la structure',
    ...customOfferer,
  }
}

export const stockFactory = (customStock = {}) => {
  return {
    bookingsQuantity: 0,
    id: 'S1',
    offerId: 'O1',
    price: 10,
    quantity: null,
    ...customStock,
  }
}
