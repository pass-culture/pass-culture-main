import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { OffererName } from 'core/Offerers/types'
import { OfferSubCategory } from 'core/Offers/types'
import { IndividualOfferVenue } from 'core/Venue/types'

import buildSubcategoryFields from './buildSubCategoryFields'

const setDefaultInitialFormValues = (
  offererNames: OffererName[],
  offererId: string | null,
  venueId: string | null,
  venueList: IndividualOfferVenue[],
  isBookingContactEnabled: boolean,
  subcategory?: OfferSubCategory
): IndividualOfferFormValues => {
  let initialOffererId = FORM_DEFAULT_VALUES.offererId

  if (offererNames.length === 1) {
    initialOffererId = offererNames[0].id.toString()
  } else if (
    offererId &&
    offererNames.find(offerer => offerer.id.toString() === offererId)
  ) {
    initialOffererId = offererId
  }

  let initialWithdrawalDetails = FORM_DEFAULT_VALUES.withdrawalDetails
  let initialAccessibility = FORM_DEFAULT_VALUES.accessibility
  const initialIsVenueVirtual = venueList.every(v => v.isVirtual)

  const venue =
    venueList.length === 1
      ? venueList[0]
      : venueList.find(venue => venue.id.toString() === venueId)

  if (venue) {
    initialAccessibility = venue.accessibility

    if (venue.withdrawalDetails) {
      initialWithdrawalDetails = venue.withdrawalDetails
    }
  }

  const { subcategoryFields } = buildSubcategoryFields(
    isBookingContactEnabled,
    subcategory
  )

  return {
    ...FORM_DEFAULT_VALUES,
    isDuo: subcategory?.canBeDuo ?? FORM_DEFAULT_VALUES.isDuo,
    categoryId: subcategory?.categoryId ?? FORM_DEFAULT_VALUES.categoryId,
    subcategoryId: subcategory?.id ?? FORM_DEFAULT_VALUES.subcategoryId,
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
