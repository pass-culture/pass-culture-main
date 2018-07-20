import moment from 'moment'

export const eventNormalizer = {
  mediations: 'mediations',
  occasions: 'occasions',
  occurences: {
    key: 'eventOccurences',
    normalizer: {
      offer: 'offers'
    }
  }
}

export const eventOccurenceNormalize = {
  venue: {
    key: 'venues',
    normalizer: venueNormalizer,
  }
}

export const thingNormalizer = {
  mediations: 'mediations',
  occasions: 'occasions'
}

export const occasionNormalizer = {
  event: {
    key: 'events',
    normalizer: eventNormalizer
  },
  thing: {
    key: 'things',
    normalizer: thingNormalizer
  },
  venue: {
    key: 'venues',
    normalizer: {
      managingOfferer: 'offerers'
    }
  }
}

export const mediationNormalizer = {
  event: {
    key: 'events',
    normalizer: eventNormalizer
  },
  thing: {
    key: 'things',
    normalizer: thingNormalizer
  }
}

export const offererNormalizer = {
  managedVenues: {
    key: 'venues',
    normalizer: {
      occasions: 'occasions',
    }
  }
}

export const venueNormalizer = {
  eventOccurences: {
    key: 'eventOccurences',
    normalizer: {
      'event': 'events'
    }
  },
  managingOfferer: {
    key: 'offerers'
  },
  offers: {
    key: 'offers',
    normalizer: {
      thing: 'things'
    }
  }
}
