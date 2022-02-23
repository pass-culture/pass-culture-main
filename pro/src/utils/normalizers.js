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
