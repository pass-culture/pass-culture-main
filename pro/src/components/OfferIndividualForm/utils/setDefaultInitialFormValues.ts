import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

import { buildVenueOptions } from '../UsefulInformations/Venue/utils'

const setDefaultInitialFormValues = (
  values: IOfferIndividualFormValues,
  offererNames: TOffererName[],
  offererId: string | null,
  venueId: string | null,
  venueList: TOfferIndividualVenue[]
): IOfferIndividualFormValues => {
  let initialOffererId = FORM_DEFAULT_VALUES.offererId

  if (offererNames.length === 1) {
    initialOffererId = offererNames[0].nonHumanizedId.toString()
  } else if (
    offererId &&
    offererNames.find(
      offerer => offerer.nonHumanizedId.toString() === offererId
    )
  ) {
    initialOffererId = offererId
  }

  const { venueOptions } = buildVenueOptions(initialOffererId, venueList)

  const initialVenueId =
    venueId ??
    (venueOptions.length === 1
      ? venueOptions[0].value
      : FORM_DEFAULT_VALUES.venueId)

  let initialWithdrawalDetails = FORM_DEFAULT_VALUES.withdrawalDetails
  let initialAccessibility = FORM_DEFAULT_VALUES.accessibility
  let initialIsVenueVirtual

  const venue = venueList.find(
    venue => venue.nonHumanizedId.toString() === initialVenueId
  )

  if (initialVenueId && venue) {
    initialAccessibility = venue.accessibility
    initialIsVenueVirtual = venue.isVirtual

    if (venue.withdrawalDetails) {
      initialWithdrawalDetails = venue.withdrawalDetails
    }
  }

  return {
    ...values,
    offererId: initialOffererId,
    venueId: String(initialVenueId),
    withdrawalDetails: initialWithdrawalDetails,
    accessibility: initialAccessibility,
    isVenueVirtual: initialIsVenueVirtual,
  }
}

export default setDefaultInitialFormValues
