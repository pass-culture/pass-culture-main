import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { AddressResponseIsNotLinkToVenueModelFactory } from 'utils/commonOffersApiFactories'
import {
  getOfferVenueFactory,
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'utils/individualApiFactories'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../constants'
import { buildInitialValues } from '../buildInitialValues'

const WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE_ENABLED = false

describe('StockThingForm::utils::buildInitialValues', () => {
  let offer: GetIndividualOfferWithAddressResponseModel
  beforeEach(() => {
    offer = getIndividualOfferFactory({
      venue: getOfferVenueFactory({ departementCode: '93' }),
    })
  })

  it('should return default values when offer have no stocks', () => {
    const initialValues = buildInitialValues(
      offer,
      [],
      WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE_ENABLED
    )
    expect(initialValues).toEqual(STOCK_THING_FORM_DEFAULT_VALUES)
  })

  it('should build form initial values from offer', () => {
    const initialValues = buildInitialValues(
      offer,
      [
        getOfferStockFactory({
          id: 1,
          remainingQuantity: 10,
          bookingsQuantity: 20,
          quantity: 40,
          bookingLimitDatetime: '2001-06-05',
          price: 12,
        }),
      ],
      WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE_ENABLED
    )
    expect(initialValues).toEqual({
      stockId: 1,
      remainingQuantity: '10',
      bookingsQuantity: '20',
      quantity: 40,
      bookingLimitDatetime: '2001-06-05',
      price: 12,
      activationCodes: [],
      activationCodesExpirationDatetime: '',
      isDuo: true,
    })
  })

  it('should normalize null values', () => {
    const initialValues = buildInitialValues(
      offer,
      [
        getOfferStockFactory({
          id: 1,
          bookingsQuantity: 20,
          remainingQuantity: undefined,
          quantity: null,
          bookingLimitDatetime: null,
          price: 12,
        }),
      ],
      WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE_ENABLED
    )
    expect(initialValues).toEqual({
      activationCodes: [],
      activationCodesExpirationDatetime: '',
      stockId: 1,
      remainingQuantity: 'unlimited',
      bookingsQuantity: '20',
      quantity: null,
      bookingLimitDatetime: '',
      price: 12,
      isDuo: true,
    })
  })

  it('should format date with good department code if FF WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE_ENABLED', () => {
    offer.address = AddressResponseIsNotLinkToVenueModelFactory({
      departmentCode: '987', // Pacific/Tahiti
    })

    const initialValues = buildInitialValues(
      offer,
      [getOfferStockFactory({ id: 8, bookingLimitDatetime: '2001-06-05' })],
      !WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE_ENABLED
    )

    expect(initialValues).toEqual({
      ...STOCK_THING_FORM_DEFAULT_VALUES,
      bookingLimitDatetime: '2001-06-04',
      isDuo: true,
      price: 10,
      quantity: 18,
      remainingQuantity: 'unlimited',
      stockId: 8,
    })
  })
})
