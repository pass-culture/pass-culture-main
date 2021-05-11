let offerId = 1
let venueId = 1
let offererId = 1
let stockId = 1

export const offerFactory = (
  customOffer = {},
  customStock = stockFactory(),
  customVenue = venueFactory()
) => {
  const stocks = customStock === null ? [] : [customStock]

  return {
    id: `OFFER${offerId++}`,
    isEvent: false,
    status: 'ACTIVE',
    stocks,
    venue: customVenue,
    ...customOffer,
  }
}

export const venueFactory = (customVenue = {}, customOfferer = offererFactory()) => {
  return {
    id: `VENUE${venueId++}`,
    managingOfferer: customOfferer,
    managingOffererId: customOfferer.id,
    name: 'Le nom du lieu',
    ...customVenue,
  }
}

export const offererFactory = (customOfferer = {}) => {
  return {
    id: `OFFERER${offererId++}`,
    name: 'La nom de la structure',
    ...customOfferer,
  }
}

export const stockFactory = (customStock = {}) => {
  return {
    bookingsQuantity: 0,
    id: `STOCK${stockId++}`,
    offerId: `OFFER${offerId}`,
    price: 10,
    quantity: null,
    activationCodes: [],
    ...customStock,
  }
}
