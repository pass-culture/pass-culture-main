import { GetOfferVenueResponseModel } from 'apiClient/v1'

let VENUE_ID = 0

export const offerVenueFactory = (
  customOfferVenue: Partial<GetOfferVenueResponseModel> = {}
): GetOfferVenueResponseModel => {
  const id = customOfferVenue.id ?? VENUE_ID++

  return {
    id,
    audioDisabilityCompliant: true,
    isVirtual: false,
    managingOfferer: {
      id: 1,
      allowedOnAdage: true,
      name: 'Le nom de l’offreur 1',
    },
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    name: `Le nom du lieu ${id}`,
    publicName: undefined,
    visualDisabilityCompliant: true,
    ...customOfferVenue,
  }
}
