import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'

const setDefaultInitialFormValues = (
  values: IOfferIndividualFormValues,
  offererNames: TOffererName[],
  offererId: string | null,
  venueId: string | null,
  venueList: TOfferIndividualVenue[]
): IOfferIndividualFormValues => {
  let initialOffererId = FORM_DEFAULT_VALUES.offererId
  if (offererNames.length === 1) {
    initialOffererId = offererNames[0]
      .id as IOfferIndividualFormValues['offererId']
  } else if (
    offererId &&
    offererNames.find(offerer => offerer.id === offererId)
  ) {
    initialOffererId = offererId
  }

  let initialVenueId = FORM_DEFAULT_VALUES.venueId
  let initialWithdrawalDetails = FORM_DEFAULT_VALUES.withdrawalDetails
  let initialAccessibility = FORM_DEFAULT_VALUES.accessibility
  let initialIsVenueVirtual

  const venue = venueList.find(venue => venue.id === venueId)
  if (venueId && venue) {
    initialVenueId = venueId
    initialAccessibility = venue.accessibility
    initialIsVenueVirtual = venue.isVirtual

    if (venue.withdrawalDetails) {
      initialWithdrawalDetails = venue.withdrawalDetails
    }
  }

  return {
    ...values,
    offererId: initialOffererId,
    venueId: initialVenueId,
    withdrawalDetails: initialWithdrawalDetails,
    accessibility: initialAccessibility,
    isVenueVirtual: initialIsVenueVirtual,
  }
}

export default setDefaultInitialFormValues
