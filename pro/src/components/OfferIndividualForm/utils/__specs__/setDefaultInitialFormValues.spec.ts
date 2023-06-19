import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

import setDefaultInitialFormValues from '../setDefaultInitialFormValues'

describe('setDefaultInitialFormValues', () => {
  let expectedInitialValues: IOfferIndividualFormValues
  let offererNames: TOffererName[]
  let offererId: string | null
  let venueId: string | null
  let venueList: TOfferIndividualVenue[]

  beforeEach(() => {
    expectedInitialValues = {
      ...FORM_DEFAULT_VALUES,
      offererId: '1',
      venueId: '1',
      isVenueVirtual: true,
      withdrawalDetails: 'détails de retrait',
      accessibility: { ...FORM_DEFAULT_VALUES.accessibility, none: true },
    }

    offererNames = [
      { name: 'offerer A', nonHumanizedId: 1 },
      { name: 'offerer B', nonHumanizedId: 2 },
    ]
    offererId = '1'
    venueId = '1'
    venueList = [
      {
        nonHumanizedId: 1,
        managingOffererId: 'AE',
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
        nonHumanizedId: 2,
        managingOffererId: 'AE',
        name: 'Venue Name 2',
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
    ]
  })

  it('should return initial values', () => {
    // given / when
    const initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      offererId,
      venueId,
      venueList
    )

    // then
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return initial values when there is only one offererName', () => {
    // given
    offererNames = [{ name: 'offerer B', nonHumanizedId: 2 }]
    offererId = '2'
    // when
    const initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      offererId,
      venueId,
      venueList
    )

    // then
    expectedInitialValues.offererId = '2'
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return venue when there is only one venue', () => {
    // given
    const venueId = null
    venueList = [venueList[0]]

    // when
    const initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      offererId,
      venueId,
      venueList
    )

    // then
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })

  it('should return initial values when there is no venueId', () => {
    // given
    const venueId = null

    // when
    const initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      offererId,
      venueId,
      venueList
    )

    // then
    expectedInitialValues.venueId = FORM_DEFAULT_VALUES.venueId
    expectedInitialValues.isVenueVirtual = undefined
    expectedInitialValues.accessibility = FORM_DEFAULT_VALUES.accessibility
    expectedInitialValues.withdrawalDetails =
      FORM_DEFAULT_VALUES.withdrawalDetails
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })
})
