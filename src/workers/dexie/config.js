const config = {
  name: "pass_culture",
  collections: [
    {
      description: 'index',
      name: 'userMediations',
      query: ({ around,
        mediationId,
        offerId
      }) => around
        ? `around=${around}`
        : (
          mediationId
            ? `mediationId=${mediationId}`
            : (offerId && `offerId=${offerId}`) || ''
        ),
      isSync: true
    },
    {
      description: 'id',
      name: 'differences'
    },
    {
      description: 'id',
      name: 'users'
    }
  ],
  version: 1
}

export default config
