export const eventNormalizer = {
  mediations: 'mediations',
  offers: 'offers',
  occurrences: {
    key: 'eventOccurrences',
    normalizer: {
      offer: 'offers',
    },
  },
}

export const thingNormalizer = {
  mediations: 'mediations',
  offers: 'offers',
}

export const offerNormalizer = {
  event: {
    key: 'events',
    normalizer: eventNormalizer,
  },
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

export const eventOccurrenceNormalize = {
  venue: {
    key: 'venues',
    normalizer: venueNormalizer,
  },
}
