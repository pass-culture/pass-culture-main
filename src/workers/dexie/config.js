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
      query: ({ around, mediationId, offerId, position }) => {
        let query = around
          ? `around=${around}`
          : mediationId
            ? `mediationId=${mediationId}`
            : (offerId && `offerId=${offerId}`) || ''
        if (position && position.coords) {
          const { latitude, longitude } = position.coords
          query = `${query}&&latitude=${latitude}&&longitude=${longitude}`
        }
        return query
      },
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
