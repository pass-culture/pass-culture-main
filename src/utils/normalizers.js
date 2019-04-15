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

export const productNormalizer = {
  offers: 'offers',
}

export const offerNormalizer = {
  mediations: 'mediations',
  product: {
    normalizer: productNormalizer,
    stateKey: 'products',
  },
  stocks: 'stocks',
  venue: {
    normalizer: {
      managingOfferer: 'offerers',
    },
    stateKey: 'venues',
  },
}

export const mediationNormalizer = {
  product: {
    normalizer: productNormalizer,
    stateKey: 'products',
  },
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
  venueProviders: 'venueProviders',
}
