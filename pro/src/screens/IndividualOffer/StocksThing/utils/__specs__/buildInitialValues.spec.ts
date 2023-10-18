import { IndividualOffer } from 'core/Offers/types'
import { offerVenueFactory } from 'utils/apiFactories'
import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../constants'
import buildInitialValues from '../buildInitialValues'

describe('StockThingForm::utils::buildInitialValues', () => {
  let offer: IndividualOffer
  beforeEach(() => {
    offer = individualOfferFactory({
      venue: offerVenueFactory({ departementCode: '93' }),
    })
  })

  it('should return default values when offer have no stocks', () => {
    offer.stocks = []
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual(STOCK_THING_FORM_DEFAULT_VALUES)
  })

  it('should build form initial values from offer', () => {
    offer.stocks = [
      individualStockFactory({
        id: 1,
        remainingQuantity: 10,
        bookingsQuantity: 20,
        quantity: 40,
        bookingLimitDatetime: '2001-06-05',
        price: 12,
      }),
    ]

    const initialValues = buildInitialValues(offer)
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
    offer.stocks = [
      individualStockFactory({
        id: 1,
        bookingsQuantity: 20,
        remainingQuantity: undefined,
        quantity: null,
        bookingLimitDatetime: null,
        price: 12,
      }),
    ]

    const initialValues = buildInitialValues(offer)
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
})
