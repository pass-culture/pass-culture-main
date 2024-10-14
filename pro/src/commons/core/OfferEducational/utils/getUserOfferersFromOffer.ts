import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'

export const getUserOfferersFromOffer = (
  offerers: GetEducationalOffererResponseModel[],
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
): GetEducationalOffererResponseModel[] => {
  if (offer === undefined) {
    return offerers
  }

  const userOfferers = offerers.filter((offerer) =>
    offerer.managedVenues.map((venue) => venue.id).includes(offer.venue.id)
  )

  return userOfferers
}
