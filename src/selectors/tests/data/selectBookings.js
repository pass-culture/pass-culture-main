const resolvedActivationOffer = {
  resolvedOffer: {
    eventOrThing: {
      type: 'EventType.ACTIVATION',
    },
  },
}

const resolvedNotActivationOffer = {
  resolvedOffer: {
    eventOrThing: {
      type: 'EventType.ANY',
    },
  },
}

const inOneDay = now => now.clone().add(1, 'days')
const inExactTwoDays = now => now.clone().add(2, 'days')
const yesterDayDate = now => now.clone().subtract(1, 'days')
const inFourDaysDate = now => now.clone().add(4, 'days')
const inTwoDaysOneSeconds = now =>
  now
    .clone()
    .add(2, 'days')
    .add(1, 'seconds')

const AllBookingsDataset = now => [
  { debugid: 'not a valid booking' },
  { debugid: 'not a valid stock', stock: {} },
  {
    stock: {
      debugid: 'is-an-activation',
      eventOccurrence: {
        beginningDatetime: inExactTwoDays(now),
      },
      ...resolvedActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-yesterday',
      eventOccurrence: {
        beginningDatetime: yesterDayDate(now),
      },
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-in-4-days',
      eventOccurrence: {
        beginningDatetime: inFourDaysDate(now),
      },
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-in-2-days-and-1-seconds',
      eventOccurrence: {
        beginningDatetime: inTwoDaysOneSeconds(now),
      },
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-in-exact-2-days',
      eventOccurrence: {
        beginningDatetime: inExactTwoDays(now),
      },
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-tomorrow',
      eventOccurrence: {
        beginningDatetime: inOneDay(now),
      },
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-exact-now',
      eventOccurrence: {
        beginningDatetime: now.clone(),
      },
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      debugid: 'not-activation-without-beginningDatetime',
      eventOccurrence: {},
      ...resolvedNotActivationOffer,
    },
  },
]

export default AllBookingsDataset
