import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'

export const setInitialFormValues = (
  values: IOfferEducationalFormValues,
  offerers: GetEducationalOffererResponseModel[],
  offererId: string | null,
  venueId: string | null
): IOfferEducationalFormValues => {
  let computedOffererId = DEFAULT_EAC_FORM_VALUES.offererId
  let computedVenueId = DEFAULT_EAC_FORM_VALUES.venueId

  if (offerers.length === 1) {
    computedOffererId = offerers[0]
      .id as IOfferEducationalFormValues['offererId']
  }

  if (offererId) {
    computedOffererId = offererId as IOfferEducationalFormValues['offererId']
  }

  if (offerers.length === 1 && offerers[0].managedVenues.length === 1) {
    computedVenueId = offerers[0].managedVenues[0]
      .id as IOfferEducationalFormValues['venueId']
  }

  if (offererId) {
    const currentOfferer = offerers.find(offerer => offerer.id === offererId)

    if (currentOfferer?.managedVenues.length === 1) {
      computedVenueId = currentOfferer.managedVenues[0]
        .id as IOfferEducationalFormValues['venueId']
    }
  }

  if (venueId) {
    computedVenueId = venueId as IOfferEducationalFormValues['venueId']
  }

  return {
    ...values,
    offererId: computedOffererId,
    venueId: computedVenueId,
  }
}
