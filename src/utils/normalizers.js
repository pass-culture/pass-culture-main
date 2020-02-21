export const myBookingsNormalizer = {
  mediation: 'mediations',
  stock: {
    normalizer: {
      offer: 'offers',
    },
    stateKey: 'stocks',
  },
}

export const bookingNormalizer = {
  mediation: 'mediations',
  stock: {
    normalizer: {
      offer: 'offers',
    },
    stateKey: 'stocks',
  },
  user: {
    isMergingDatum: true,
    stateKey: 'users',
  },
}

export const favoriteNormalizer = {
  firstMatchingBooking: 'bookings',
  mediation: 'mediations',
  offer: {
    normalizer: {
      stocks: 'stocks',
    },
    stateKey: 'offers',
  },
}

export const recommendationNormalizer = {
  bookings: {
    normalizer: {
      stock: 'stocks',
    },
    stateKey: 'bookings',
  },
  mediation: 'mediations',
  offer: {
    normalizer: {
      favorites: 'favorites',
      stocks: 'stocks',
    },
    stateKey: 'offers',
  },
}

export const offerNormalizer = {
  activeMediation: {
    stateKey: 'mediations',
  },
  firstMatchingBooking: 'bookings',
  stocks: {
    stateKey: 'stocks',
    normalizer: {
      bookings: 'bookings',
    },
  },
}
