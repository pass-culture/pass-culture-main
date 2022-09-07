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
      accessibility: {
        audio: false,
        mental: false,
        motor: false,
        none: true,
        visual: false,
      },
      author: '',
      bookingEmail: '',
      categoryId: '',
      description: '',
      durationMinutes: '',
      isEvent: false,
      isNational: false,
      isDuo: true,
      isbn: '',
      musicSubType: '',
      musicType: '',
      name: '',
      offererId: 'A',
      performer: '',
      receiveNotificationEmails: false,
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      subCategoryFields: [],
      subcategoryId: '',
      venueId: 'C',
      visa: '',
      withdrawalDelay: undefined,
      withdrawalDetails: 'détails de retrait',
      withdrawalType: undefined,
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
    expectedInitialValues.accessibility = FORM_DEFAULT_VALUES.accessibility
    expectedInitialValues.withdrawalDetails =
      FORM_DEFAULT_VALUES.withdrawalDetails
    expect(initialValues).toStrictEqual(expectedInitialValues)
  })
})
