import '@testing-library/jest-dom'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'

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
      offererId: 'A',
      venueId: 'C',
      isVenueVirtual: true,
      withdrawalDetails: 'détails de retrait',
      accessibility: { ...FORM_DEFAULT_VALUES.accessibility, none: true },
    }

    offererNames = [
      { id: 'A', name: 'offerer A' },
      { id: 'B', name: 'offerer B' },
    ]
    offererId = 'A'
    venueId = 'C'
    venueList = [
      {
        id: 'C',
        managingOffererId: 'A',
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
    offererNames = [{ id: 'B', name: 'offerer B' }]

    // when
    const initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      offererId,
      venueId,
      venueList
    )

    // then
    expectedInitialValues.offererId = 'B'
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
