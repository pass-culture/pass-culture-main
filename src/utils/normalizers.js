export const bookingNormalizer = {
  stock: {
    normalizer: {
      resolvedOffer: {
        normalizer: {
          event: 'events',
          thing: 'things',
        },
        stateKey: 'offers',
      },
    },
    stateKey: 'stocks',
  },
  user: 'users',
}

export const eventNormalizer = {
  offers: 'offers',
}

export const thingNormalizer = {
  offers: 'offers',
}

export const offerNormalizer = {
  event: {
    normalizer: eventNormalizer,
    stateKey: 'events',
  },
  mediations: 'mediations',
  stocks: 'stocks',
  thing: {
    normalizer: thingNormalizer,
    stateKey: 'things',
  },
  venue: {
    normalizer: {
      managingOfferer: 'offerers',
    },
    stateKey: 'venues',
  },
}

export const mediationNormalizer = {
  event: {
    normalizer: eventNormalizer,
    stateKey: 'events',
  },
  thing: {
    normalizer: thingNormalizer,
    stateKey: 'things',
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
      thing: 'things',
    },
    stateKey: 'offers',
  },
  venueProviders: 'venueProviders',
}
