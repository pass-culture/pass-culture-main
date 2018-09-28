export const bookingNormalizer = {
  stock: {
    key: 'stocks',
    normalizer: {
      eventOccurrence: 'eventOccurrences',
      resolvedOffer: {
        key: 'offers',
        normalizer: {
          event: 'events',
          thing: 'things',
        },
      },
    },
  },
}

export const eventNormalizer = {
  offers: 'offers',
}

export const thingNormalizer = {
  offers: 'offers',
}

export const offerNormalizer = {
  event: {
    key: 'events',
    normalizer: eventNormalizer,
  },
  eventOccurrences: 'eventOccurrences',
  mediations: 'mediations',
  stocks: 'stocks',
  thing: {
    key: 'things',
    normalizer: thingNormalizer,
  },
  venue: {
    key: 'venues',
    normalizer: {
      managingOfferer: 'offerers',
    },
  },
}

export const mediationNormalizer = {
  event: {
    key: 'events',
    normalizer: eventNormalizer,
  },
  thing: {
    key: 'things',
    normalizer: thingNormalizer,
  },
}

export const offererNormalizer = {
  managedVenues: {
    key: 'venues',
    normalizer: {
      offers: 'offers',
    },
  },
}

export const venueNormalizer = {
  eventOccurrences: {
    key: 'eventOccurrences',
    normalizer: {
      event: 'events',
    },
  },
  offers: {
    key: 'offers',
    normalizer: {
      thing: 'things',
    },
  },
}

export const eventOccurrenceNormalizer = {
  venue: {
    key: 'venues',
    normalizer: venueNormalizer,
  },
}
