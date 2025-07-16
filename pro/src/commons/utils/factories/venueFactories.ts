import { GetOfferVenueResponseModel } from 'apiClient/v1'

let VENUE_ID = 0

export const offerVenueFactory = (
  customOfferVenue: Partial<GetOfferVenueResponseModel> = {}
): GetOfferVenueResponseModel => {
  const currentVenueId = VENUE_ID++

  return {
    id: currentVenueId,
    audioDisabilityCompliant: true,
    isVirtual: false,
    managingOfferer: {
      id: 1,
      allowedOnAdage: true,
      name: `Gestionnaire de la venue ${currentVenueId}`,
    },
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    name: `Le nom du lieu ${currentVenueId}`,
    publicName: undefined,
    visualDisabilityCompliant: true,
    ...customOfferVenue,
  }
}
