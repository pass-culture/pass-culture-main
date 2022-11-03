import { STOCK_THING_FORM_DEFAULT_VALUES } from 'components/StockThingForm/constants'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'

import buildInitialValues from '../buildInitialValues'

describe('StockThingForm::utils::buildInitialValues', () => {
  let offer: IOfferIndividual
  beforeEach(() => {
    offer = {} as IOfferIndividual
  })

  it('should return default values when offer have no stocks', () => {
    offer.stocks = []
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual(STOCK_THING_FORM_DEFAULT_VALUES)
  })

  it('should build form initial values from offer', () => {
    offer.stocks = [
      {
        id: 'STOCK_ID',
        remainingQuantity: 10,
        bookingsQuantity: 20,
        quantity: 40,
        bookingLimitDatetime: '2001-06-05',
        price: 12,
      } as IOfferIndividualStock,
    ]
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual({
      stockId: 'STOCK_ID',
      remainingQuantity: '10',
      bookingsQuantity: '20',
      quantity: '40',
      bookingLimitDatetime: new Date('2001-06-05'),
      price: '12',
    })
  })

  it('should normalize null values', () => {
    offer.stocks = [
      {
        id: 'STOCK_ID',
        bookingsQuantity: 20,
        quantity: null,
        bookingLimitDatetime: null,
        price: 12,
      } as IOfferIndividualStock,
    ]
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual({
      stockId: 'STOCK_ID',
      remainingQuantity: 'unlimited',
      bookingsQuantity: '20',
      quantity: '',
      bookingLimitDatetime: null,
      price: '12',
    })
  })
})
