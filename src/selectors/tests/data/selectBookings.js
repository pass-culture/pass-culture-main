const resolvedOffer = {
  resolvedOffer: {
    eventOrThing: {
      type: 'EventType.ACTIVATION',
    },
    offerId: 1234,
  },
}

const AllBookingsDataset = now => [
  { debugid: 'not a valid boking' },
  { debugid: 'not a valid stock', stock: {} },
  {
    stock: {
      eventOccurrence: {
        debugid: 'not-a-valid-eventOccurrence',
      },
      ...resolvedOffer,
    },
  },
  {
    stock: {
      eventOccurrence: {
        beginningDatetime: now.clone().subtract(1, 'days'),
        debugid: 'yesterday',
      },
      ...resolvedOffer,
    },
  },
  {
    stock: {
      eventOccurrence: {
        beginningDatetime: now.clone().add(4, 'days'),
        debugid: 'in-4-days',
      },
      ...resolvedOffer,
    },
  },
  {
    stock: {
      eventOccurrence: {
        beginningDatetime: now
          .clone()
          .add(2, 'days')
          .add(1, 'seconds'),
        debugid: 'in-2-days-and-1-seconds',
      },
      ...resolvedOffer,
    },
  },
  {
    stock: {
      eventOccurrence: {
        beginningDatetime: now.clone().add(2, 'days'),
        debugid: 'in-exact-2-days',
      },
      ...resolvedOffer,
    },
  },
  {
    stock: {
      eventOccurrence: {
        beginningDatetime: now.clone().add(1, 'days'),
        debugid: 'tomorrow',
      },
      ...resolvedOffer,
    },
  },
]

export default AllBookingsDataset
