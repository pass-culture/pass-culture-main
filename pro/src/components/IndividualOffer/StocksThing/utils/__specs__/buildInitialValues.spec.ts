import { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  getOfferVenueFactory,
} from '@/commons/utils/factories/individualApiFactories'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../constants'
import { buildInitialValues } from '../buildInitialValues'

describe('StockThingForm::utils::buildInitialValues', () => {
  let offer: GetIndividualOfferWithAddressResponseModel
  beforeEach(() => {
    offer = getIndividualOfferFactory({
      venue: getOfferVenueFactory({ departementCode: '93' }),
    })
  })

  it('should return default values when offer have no stocks', () => {
    const initialValues = buildInitialValues(offer, [])
    expect(initialValues).toEqual(STOCK_THING_FORM_DEFAULT_VALUES)
  })

  it('should build form initial values from offer', () => {
    const initialValues = buildInitialValues(offer, [
      getOfferStockFactory({
        id: 1,
        remainingQuantity: 10,
        bookingsQuantity: 20,
        quantity: 40,
        bookingLimitDatetime: '2001-06-05',
        price: 12,
      }),
    ])
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
    const initialValues = buildInitialValues(offer, [
      getOfferStockFactory({
        id: 1,
        bookingsQuantity: 20,
        remainingQuantity: undefined,
        quantity: null,
        bookingLimitDatetime: null,
        price: 12,
      }),
    ])
    expect(initialValues).toEqual({
      activationCodes: [],
      activationCodesExpirationDatetime: '',
      stockId: 1,
      remainingQuantity: 'unlimited',
      bookingsQuantity: '20',
      bookingLimitDatetime: '',
      quantity: undefined,
      price: 12,
      isDuo: true,
    })
  })

  it('should format date with good department code', () => {
    offer.address = getAddressResponseIsLinkedToVenueModelFactory({
      departmentCode: '987', // Pacific/Tahiti
    })

    const initialValues = buildInitialValues(offer, [
      getOfferStockFactory({ id: 8, bookingLimitDatetime: '2001-06-05' }),
    ])

    expect(initialValues).toEqual({
      ...STOCK_THING_FORM_DEFAULT_VALUES,
      bookingLimitDatetime: '2001-06-04', // Tahiti is UTC-10 so we expect here 1 day earlier
      isDuo: true,
      price: 10,
      quantity: 18,
      remainingQuantity: 'unlimited',
      stockId: 8,
    })
  })
})
