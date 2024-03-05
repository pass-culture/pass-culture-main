import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { buildAccessibilityFormValues } from 'pages/VenueEdition/setInitialFormValues'

import buildSubcategoryFields from './buildSubCategoryFields'

const setDefaultInitialFormValues = (
  offererNames: GetOffererNameResponseModel[],
  offererId: string | null,
  venueId: string | null,
  venueList: VenueListItemResponseModel[],
  isBookingContactEnabled: boolean
): IndividualOfferFormValues => {
  let initialOffererId = FORM_DEFAULT_VALUES.offererId

  if (offererNames.length === 1) {
    initialOffererId = offererNames[0].id.toString()
  } else if (
    offererId &&
    offererNames.find((offerer) => offerer.id.toString() === offererId)
  ) {
    initialOffererId = offererId
  }

  let initialWithdrawalDetails = FORM_DEFAULT_VALUES.withdrawalDetails
  let initialAccessibility = FORM_DEFAULT_VALUES.accessibility
  const initialIsVenueVirtual = venueList.every((v) => v.isVirtual)

  const venue =
    venueList.length === 1
      ? venueList[0]
      : venueList.find((venue) => venue.id.toString() === venueId)

  if (venue) {
    initialAccessibility = buildAccessibilityFormValues(venue)

    if (venue.withdrawalDetails) {
      initialWithdrawalDetails = venue.withdrawalDetails
    }
  }

  const { subcategoryFields } = buildSubcategoryFields(isBookingContactEnabled)

  return {
    ...FORM_DEFAULT_VALUES,
    isDuo: FORM_DEFAULT_VALUES.isDuo,
    categoryId: FORM_DEFAULT_VALUES.categoryId,
    subcategoryId: FORM_DEFAULT_VALUES.subcategoryId,
    subCategoryFields: subcategoryFields
      ? subcategoryFields
      : FORM_DEFAULT_VALUES.subCategoryFields,
    offererId: initialOffererId,
    venueId: venue?.id ? String(venue?.id) : FORM_DEFAULT_VALUES.venueId,
    withdrawalDetails: initialWithdrawalDetails,
    accessibility: initialAccessibility,
    isVenueVirtual: initialIsVenueVirtual,
  }
}

export default setDefaultInitialFormValues
