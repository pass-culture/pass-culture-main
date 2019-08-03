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
  user: {
    isMergingDatum: true,
    stateKey: 'users',
  },
}

export const favoriteNormalizer = {
  firstMatchingBooking: 'bookings',
  mediation: 'mediations',
  offer: 'offers',
}

export const recommendationNormalizer = {
  bookings: 'bookings',
  mediation: 'mediations',
  offer: {
    normalizer: {
      favorites: 'favorites',
    },
    stateKey: 'offers',
  },
}
