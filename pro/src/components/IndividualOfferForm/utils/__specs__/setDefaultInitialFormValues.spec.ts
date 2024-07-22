import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { FORM_DEFAULT_VALUES } from 'components/IndividualOfferForm/constants'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import {
  getOffererNameFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'

import { setDefaultInitialFormValues } from '../setDefaultInitialFormValues'

describe('setDefaultInitialFormValues', () => {
  let expectedInitialValues: IndividualOfferFormValues
  let offererNames: GetOffererNameResponseModel[]
  let offererId: string | null
  let venueId: string | null
  let venueList: VenueListItemResponseModel[]
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
      getOffererNameFactory({ name: 'offerer A', id: 1 }),
      getOffererNameFactory({ name: 'offerer B', id: 2 }),
    ]
    offererId = '1'
    venueId = '1'
    venueList = [
      venueListItemFactory({
        id: 1,
        isVirtual: true,
        name: 'Venue Name',
        withdrawalDetails: 'détails de retrait',
      }),
      venueListItemFactory({
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
    offererNames = [getOffererNameFactory({ name: 'offerer B', id: 2 })]
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
    venueList = [venueList[0]!]

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
})
