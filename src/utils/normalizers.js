export const bookingNormalizer = {
  stock: {
    normalizer: {
      eventOccurrence: 'eventOccurrences',
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
  eventOccurrences: 'eventOccurrences',
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
  eventOccurrences: {
    normalizer: {
      event: 'events',
    },
    stateKey: 'eventOccurrences',
  },
  managingOfferer: 'offerers',
  offers: {
    normalizer: {
      thing: 'things',
    },
    stateKey: 'offers',
  },
  venueProviders: 'venueProviders',
}

export const eventOccurrenceNormalizer = {
  venue: {
    normalizer: venueNormalizer,
    stateKey: 'venues',
  },
}
