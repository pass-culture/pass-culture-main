export const bookingNormalizer = {
  stock: {
    normalizer: {
      resolvedOffer: {
        normalizer: {
          product: 'products',
        },
        stateKey: 'offers',
      },
    },
    stateKey: 'stocks',
  },
  user: 'users',
}

export const offererNormalizer = {
  managedVenues: {
    normalizer: {
      offers: 'offers',
    },
    stateKey: 'venues',
  },
}

export const venueNormalizer = {
  managingOfferer: 'offerers',
  offers: {
    normalizer: {
      product: 'products',
    },
    stateKey: 'offers',
  },
}
