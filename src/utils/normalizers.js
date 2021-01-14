export const myBookingsNormalizer = {
  stock: {
    normalizer: {
      offer: {
        normalizer: {
          stocks: 'stocks',
        },
        stateKey: 'offers',
      },
    },
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
}

export const favoriteNormalizer = {
  booking: 'bookings',
  offer: {
    normalizer: {
      stocks: 'stocks',
    },
    stateKey: 'offers',
  },
}

export const offerNormalizer = {
  activeMediation: {
    stateKey: 'mediations',
  },
  stocks: {
    stateKey: 'stocks',
    normalizer: {
      bookings: 'bookings',
    },
  },
}
