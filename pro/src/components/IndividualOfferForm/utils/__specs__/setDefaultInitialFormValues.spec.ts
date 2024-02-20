import { GetOffererNameResponseModel } from 'apiClient/v1'
import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import {
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
} from 'utils/individualApiFactories'

import setDefaultInitialFormValues from '../setDefaultInitialFormValues'

describe('setDefaultInitialFormValues', () => {
  let expectedInitialValues: IndividualOfferFormValues
  let offererNames: GetOffererNameResponseModel[]
  let offererId: string | null
  let venueId: string | null
  let venueList: IndividualOfferVenueItem[]
  const isBookingContactEnabled = true

  beforeEach(() => {
    expectedInitialValues = {
      ...FORM_DEFAULT_VALUES,
      offererId: '1',
      venueId: '1',
      isVenueVirtual: false,
      withdrawalDetails: 'détails de retrait',
      accessibility: {
        visual: true,
        mental: true,
        motor: true,
        audio: true,
        none: false,
      },
    }

    offererNames = [
      { name: 'offerer A', id: 1 },
      { name: 'offerer B', id: 2 },
    ]
    offererId = '1'
    venueId = '1'
    venueList = [
      individualOfferVenueItemFactory({
        id: 1,
        isVirtual: true,
        name: 'Venue Name',
        withdrawalDetails: 'détails de retrait',
      }),
      individualOfferVenueItemFactory({
        id: 2,
        name: 'Venue Name 2',
        isVirtual: false,
        withdrawalDetails: 'détails de retrait',
      }),
    ]
  })

  it('should return initial values', () => {
    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      isBookingContactEnabled
    )

    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return initial values when there is only one offererName', () => {
    offererNames = [{ name: 'offerer B', id: 2 }]
    offererId = '2'

    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      isBookingContactEnabled
    )

    expectedInitialValues.offererId = '2'
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return venue when there is only one venue', () => {
    const venueId = null
    venueList = [venueList[0]]

    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      isBookingContactEnabled
    )

    expectedInitialValues.isVenueVirtual = true
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return initial values when there is no venueId', () => {
    const venueId = null

    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      isBookingContactEnabled
    )

    expectedInitialValues.venueId = FORM_DEFAULT_VALUES.venueId
    expectedInitialValues.isVenueVirtual = false
    expectedInitialValues.accessibility = FORM_DEFAULT_VALUES.accessibility
    expectedInitialValues.withdrawalDetails =
      FORM_DEFAULT_VALUES.withdrawalDetails
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return initial values with subcategory', () => {
    const subcategory = individualOfferSubCategoryFactory({
      canBeDuo: true,
    })

    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      isBookingContactEnabled,
      subcategory
    )

    expect(initialValues.subcategoryId).toStrictEqual(subcategory.id)
    expect(initialValues.categoryId).toStrictEqual(subcategory.categoryId)
    expect(initialValues.subCategoryFields).toStrictEqual([
      ...subcategory.conditionalFields,
      'isDuo',
    ])
  })

  it('should return subCategoryFields for subcategory who can be withrawable', () => {
    const subcategory = individualOfferSubCategoryFactory({
      canBeDuo: true,
      canBeWithdrawable: true,
    })

    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      isBookingContactEnabled,
      subcategory
    )

    expect(initialValues.subCategoryFields).toStrictEqual([
      ...subcategory.conditionalFields,
      'isDuo',
      'withdrawalType',
      'withdrawalDelay',
      'bookingContact',
    ])
  })
})
