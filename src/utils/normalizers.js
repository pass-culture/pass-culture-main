export const bookingNormalizer = {
  recommendation: {
    normalizer: {
      mediation: 'mediations',
      offer: {
        normalizer: {
          favorites: 'favorites',
        },
        stateKey: 'offers',
      },
    },
    stateKey: 'recommendations',
  },
  stock: {
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
  bookings: 'bookings',
  mediation: 'mediations',
  offer: {
    normalizer: {
      favorites: 'favorites',
      stocks: 'stocks',
    },
    stateKey: 'offers',
  },
}
