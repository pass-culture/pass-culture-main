import * as pcapi from 'repository/pcapi/pcapi'

export const bulkFakeApiCreateOrEditStock = ({ ...stockIds }) =>
  jest.spyOn(pcapi, 'bulkCreateOrEditStock').mockResolvedValue([stockIds])

export const getFakeApiUserValidatedOfferersNames = ({ ...offerers }) =>
  jest.spyOn(pcapi, 'getUserValidatedOfferersNames').mockResolvedValue([offerers])

export const getFakeApiVenuesForOfferer = ({ ...venues }) =>
  jest.spyOn(pcapi, 'getVenuesForOfferer').mockResolvedValue([venues])

export const loadFakeApiOffer = offer => jest.spyOn(pcapi, 'loadOffer').mockResolvedValue(offer)

export const loadFakeApiStocks = stocks =>
  jest.spyOn(pcapi, 'loadStocks').mockResolvedValue({ stocks })

export const loadFakeApiVenueStats = venue =>
  jest.spyOn(pcapi, 'getVenueStats').mockResolvedValue(venue)

export const generateFakeOffererApiKey = apiKey =>
  jest.spyOn(pcapi, 'generateOffererApiKey').mockResolvedValue(apiKey)

export const failToGenerateOffererApiKey = () =>
  jest.spyOn(pcapi, 'generateOffererApiKey').mockRejectedValue(null)

export const loadFakeApiTypes = () => {
  const types = [
    {
      appLabel: 'Cinéma',
      conditionalFields: ['author', 'visa', 'stageDirector'],
      description:
        "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c'était plutôt cette exposition qui allait faire son cinéma ?",
      isActive: true,
      offlineOnly: true,
      onlineOnly: false,
      proLabel: 'Cinéma - projections et autres évènements',
      sublabel: 'Regarder',
      type: 'Event',
      value: 'EventType.CINEMA',
    },
    {
      appLabel: 'Film',
      canExpire: true,
      conditionalFields: [],
      description:
        "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c'était plutôt cette exposition qui allait faire son cinéma ?",
      isActive: true,
      offlineOnly: false,
      onlineOnly: false,
      proLabel: 'Audiovisuel - films sur supports physiques et VOD',
      sublabel: 'Regarder',
      type: 'Thing',
      value: 'ThingType.AUDIOVISUEL',
    },
  ]

  jest.spyOn(pcapi, 'loadTypes').mockResolvedValue(types)

  return types
}

export const loadFakeApiVenue = venue => {
  jest.spyOn(pcapi, 'getVenue').mockResolvedValueOnce(venue)

  return {
    resolvingVenuePromise: Promise.resolve(venue),
  }
}
