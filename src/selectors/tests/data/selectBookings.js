const resolvedActivationOffer = {
  resolvedOffer: {
    eventOrThing: {
      type: 'EventType.ACTIVATION',
    },
    type: 'EventType.ACTIVATION',
  },
}

const resolvedNotActivationOffer = {
  resolvedOffer: {
    eventOrThing: {
      type: 'EventType.ANY',
    },
    type: 'EventType.ANY',
  },
}

const inOneDay = now => now.clone().add(1, 'days')
export const inExactTwoDays = now => now.clone().add(2, 'days')
const yesterDayDate = now => now.clone().subtract(1, 'days')
const inFourDaysDate = now => now.clone().add(4, 'days')
const inTwoDaysOneSeconds = now =>
  now
    .clone()
    .add(2, 'days')
    .add(1, 'seconds')

export const allBookingsDataset = now => [
  { debugid: 'not a valid booking' },
  { debugid: 'not a valid stock', stock: {} },
  {
    stock: {
      beginningDatetime: inExactTwoDays(now),
      debugid: 'is-an-activation',
      ...resolvedActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: yesterDayDate(now),
      debugid: 'not-activation-yesterday',
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: inFourDaysDate(now),
      debugid: 'not-activation-in-4-days',
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: inTwoDaysOneSeconds(now),
      debugid: 'not-activation-in-2-days-and-1-seconds',
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: inExactTwoDays(now),
      debugid: 'not-activation-in-exact-2-days',
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: inOneDay(now),
      debugid: 'not-activation-tomorrow',
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: now.clone(),
      debugid: 'not-activation-exact-now',
      ...resolvedNotActivationOffer,
    },
  },
  {
    stock: {
      beginningDatetime: null,
      debugid: 'not-activation-without-beginningDatetime',
      ...resolvedNotActivationOffer,
    },
  },
]
