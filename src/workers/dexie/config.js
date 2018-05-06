const config = {
  name: 'pass_culture',
  collections: [
    // NECESSARY FOR DOING DIFF PUSH PULL
    {
      description: 'id',
      name: 'differences',
    },
    // SPECIFIC COLLECTIONS
    {
      description: 'id',
      name: 'recommendations',
      query: ({ around, mediationId, offerId }) =>
        around
          ? `around=${around}`
          : mediationId
            ? `mediationId=${mediationId}`
            : (offerId && `offerId=${offerId}`) || '',
      isSync: true,
    },
    {
      description: 'id',
      name: 'bookings',
      isPullOnly: true,
    },
    {
      description: 'id',
      name: 'users',
    },
  ],
  version: 1,
}

export default config
