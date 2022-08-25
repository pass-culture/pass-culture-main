let offerId = 1
let venueId = 1
let offererId = 1
let stockId = 1
let bookingId = 1

export const collectiveOfferFactory = (
  customCollectiveOffer = {},
  customStock = collectiveStockFactory() || null,
  customVenue = venueFactory()
) => {
  const stocks = customStock === null ? [] : [customStock]
  const currentOfferId = offerId++

  return {
    id: `OFFER${currentOfferId}`,
    name: `Le nom de l'offre ${currentOfferId}`,
    isActive: true,
    isEditable: true,
    isEvent: true,
    isFullyBooked: false,
    isThing: false,
    nonHumanizedId: currentOfferId,
    status: 'ACTIVE',
    stocks,
    venue: customVenue,
    hasBookingLimitDatetimesPassed: false,
    isEducational: true,
    ...customCollectiveOffer,
  }
}

export const collectiveStockFactory = (customStock = {}) => {
  return {
    bookingsQuantity: 0,
    id: `STOCK${stockId++}`,
    offerId: `OFFER${offerId}`,
    price: 100,
    quantity: 1,
    remainingQuantity: 1,
    beginningDatetime: new Date('2021-10-15T12:00:00Z'),
    bookingLimitdatetime: new Date('2021-09-15T12:00:00Z'),
    ...customStock,
  }
}

export const offerFactory = (
  customOffer = {},
  customStock = stockFactory() || null,
  customVenue = venueFactory()
) => {
  const stocks = customStock === null ? [] : [customStock]
  const currentOfferId = offerId++

  return {
    id: `OFFER${currentOfferId}`,
    name: `Le nom de l'offre ${currentOfferId}`,
    isActive: true,
    isEditable: true,
    isEvent: false,
    isFullyBooked: false,
    isThing: true,
    nonHumanizedId: currentOfferId,
    status: 'ACTIVE',
    stocks,
    venue: customVenue,
    hasBookingLimitDatetimesPassed: false,
    isEducational: false,
    ...customOffer,
  }
}

export const venueFactory = (
  customVenue = {},
  customOfferer = offererFactory()
) => {
  const currentVenueId = venueId++
  return {
    address: 'Ma Rue',
    city: 'Ma Ville',
    id: `VENUE${currentVenueId}`,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    managingOfferer: customOfferer,
    managingOffererId: customOfferer.id,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    offererName: 'Ma structure',
    departementCode: '973',
    ...customVenue,
  }
}

export const offererFactory = (customOfferer = {}) => {
  const currentOffererId = offererId++
  return {
    id: `OFFERER${currentOffererId}`,
    name: `La nom de la structure ${currentOffererId}`,
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
    remainingQuantity: 2,
    ...customStock,
  }
}

export const bookingRecapFactory = (customBookingRecap = {}) => {
  const offerer = offererFactory()
  const offer = offerFactory()
  const venue = venueFactory()

  return {
    beneficiary: {
      email: 'user@example.com',
      firstname: 'First',
      lastname: 'Last',
      phonenumber: '0606060606',
    },
    booking_amount: 0,
    booking_date: '2020-04-12T19:31:12Z',
    booking_is_duo: false,
    booking_status: 'booked',
    booking_status_history: [
      {
        date: '2020-04-12T19:31:12Z',
        status: 'booked',
      },
    ],
    booking_token: `TOKEN${bookingId++}`,
    offerer: {
      name: offerer.name,
    },
    stock: {
      offer_identifier: offer.id,
      offer_name: offer.name,
      type: 'thing',
    },
    venue: {
      venue_identifier: venue.id,
      is_virtual: venue.isVirtual,
      name: venue.name,
    },
    ...customBookingRecap,
  }
}
