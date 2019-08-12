const resolvedActivationOffer = {
  resolvedOffer: {
    product: {
      type: 'EventType.ACTIVATION',
    },
    type: 'EventType.ACTIVATION',
  },
}

const resolvedNotActivationOffer = {
  resolvedOffer: {
    product: {
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

export const allBookingsDataset = () => [
  {
    id: 'b1',
    stockId: 's1',
  },
  {
    id: 'b2',
    stockId: 's2',
  },
  {
    id: 'b3',
    stockId: 's3',
  },
  {
    id: 'b4',
    stockId: 's4',
  },
  {
    id: 'b5',
    stockId: 's5',
  },
  {
    id: 'b6',
    stockId: 's6',
  },
  {
    id: 'b7',
    stockId: 's7',
  },
  {
    id: 'b8',
    stockId: 's8',
  },
]

export const allStocksDataset = now => [
  {
    id: 's1',
    beginningDatetime: inExactTwoDays(now),
    debugid: 'is-an-activation',
    ...resolvedActivationOffer,
  },
  {
    id: 's2',
    beginningDatetime: yesterDayDate(now),
    debugid: 'not-activation-yesterday',
    ...resolvedNotActivationOffer,
  },
  {
    id: 's3',
    beginningDatetime: inFourDaysDate(now),
    debugid: 'not-activation-in-4-days',
    ...resolvedNotActivationOffer,
  },
  {
    id: 's4',
    beginningDatetime: inTwoDaysOneSeconds(now),
    debugid: 'not-activation-in-2-days-and-1-seconds',
    ...resolvedNotActivationOffer,
  },
  {
    id: 's5',
    beginningDatetime: inExactTwoDays(now),
    debugid: 'not-activation-in-exact-2-days',
    ...resolvedNotActivationOffer,
  },
  {
    id: 's6',
    beginningDatetime: inOneDay(now),
    debugid: 'not-activation-tomorrow',
    ...resolvedNotActivationOffer,
  },
  {
    id: 's7',
    beginningDatetime: now.clone(),
    debugid: 'not-activation-exact-now',
    ...resolvedNotActivationOffer,
  },
  {
    id: 's8',
    beginningDatetime: null,
    debugid: 'not-activation-without-beginningDatetime',
    ...resolvedNotActivationOffer,
  },
]
