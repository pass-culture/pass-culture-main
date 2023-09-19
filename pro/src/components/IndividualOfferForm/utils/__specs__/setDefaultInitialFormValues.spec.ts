import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { OffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { IndividualOfferVenue } from 'core/Venue/types'

import setDefaultInitialFormValues from '../setDefaultInitialFormValues'

describe('setDefaultInitialFormValues', () => {
  let expectedInitialValues: IndividualOfferFormValues
  let offererNames: OffererName[]
  let offererId: string | null
  let venueId: string | null
  let venueList: IndividualOfferVenue[]

  beforeEach(() => {
    expectedInitialValues = {
      ...FORM_DEFAULT_VALUES,
      offererId: '1',
      venueId: '1',
      isVenueVirtual: false,
      withdrawalDetails: 'détails de retrait',
      accessibility: { ...FORM_DEFAULT_VALUES.accessibility, none: true },
    }

    offererNames = [
      { name: 'offerer A', id: 1 },
      { name: 'offerer B', id: 2 },
    ]
    offererId = '1'
    venueId = '1'
    venueList = [
      {
        id: 1,
        managingOffererId: 1,
        name: 'Venue Name',
        isVirtual: true,
        withdrawalDetails: 'détails de retrait',
        accessibility: {
          visual: false,
          audio: false,
          motor: false,
          mental: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
      {
        id: 2,
        managingOffererId: 1,
        name: 'Venue Name 2',
        isVirtual: false,
        withdrawalDetails: 'détails de retrait',
        accessibility: {
          visual: false,
          audio: false,
          motor: false,
          mental: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
    ]
  })

  it('should return initial values', () => {
    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList
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
      venueList
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
      venueList
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
      venueList
    )

    expectedInitialValues.venueId = FORM_DEFAULT_VALUES.venueId
    expectedInitialValues.isVenueVirtual = false
    expectedInitialValues.accessibility = FORM_DEFAULT_VALUES.accessibility
    expectedInitialValues.withdrawalDetails =
      FORM_DEFAULT_VALUES.withdrawalDetails
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return initial values with subcategory', () => {
    const subcategory = {
      id: 'subcategoryId',
      categoryId: 'categoryId',
      proLabel: 'Sous catégorie',
      isEvent: false,
      conditionalFields: ['lapin', 'moustache'],
      canBeDuo: true,
      canBeEducational: false,
      canBeWithdrawable: false,
      onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
      isSelectable: true,
    }

    const initialValues = setDefaultInitialFormValues(
      offererNames,
      offererId,
      venueId,
      venueList,
      subcategory
    )

    expect(initialValues.subcategoryId).toStrictEqual(subcategory.id)
    expect(initialValues.categoryId).toStrictEqual(subcategory.categoryId)
    expect(initialValues.subCategoryFields).toStrictEqual(
      subcategory.conditionalFields
    )
  })
})
