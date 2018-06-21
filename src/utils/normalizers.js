export const eventNormalizer = {
  mediations: 'mediations',
  occasions: 'occasions',
  occurences: {
    key: 'eventOccurences'
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
  venue: 'venues'
}

export const offererNormalizer = {}

export const venueNormalizer = {}
