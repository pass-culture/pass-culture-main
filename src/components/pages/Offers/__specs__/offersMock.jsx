const mockedOffers = [
  {
    id: 'M4',
    activeMediation: {
      id: 'HA',
      isActive: true,
      thumbUrl: 'https://url.to/thumb',
    },
    isActive: true,
    isEditable: true,
    isEvent: true,
    isThing: false,
  },
  {
    id: 'GH',
    activeMediation: null,
    isActive: true,
    isEvent: true,
    isThing: false,
  },
  {
    id: 'XY',
    activeMediation: {
      id: 'HA',
      isActive: true,
      thumbUrl: 'https://url.to/thumb',
    },
    isActive: false,
    isEvent: true,
    isThing: false,
  },
  {
    id: 'TL',
    activeMediation: {
      id: 'HA',
      isActive: true,
      thumbUrl: 'https://url.to/thumb',
    },
    isActive: true,
    isEditable: false,
    isEvent: true,
    isThing: false,
  },
  {
    id: 'THING',
    activeMediation: {
      id: 'HA',
      isActive: true,
      thumbUrl: 'https://url.to/thumb',
    },
    isActive: true,
    isEditable: true,
    isEvent: false,
    isThing: true,
  },
]

export default mockedOffers
