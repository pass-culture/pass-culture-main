import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../'
import buildInitialValues from '../buildInitialValues'

describe('StockThingForm::utils::buildInitialValues', () => {
  let offer: IOfferIndividual
  beforeEach(() => {
    offer = { venue: { departmentCode: '93' } } as IOfferIndividual
  })

  it('should return default values when offer have no stocks', () => {
    offer.stocks = []
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual(STOCK_THING_FORM_DEFAULT_VALUES)
  })

  it('should build form initial values from offer', () => {
    offer.stocks = [
      {
        nonHumanizedId: 1,
        remainingQuantity: 10,
        bookingsQuantity: 20,
        quantity: 40,
        bookingLimitDatetime: '2001-06-05',
        price: 12,
      } as IOfferIndividualStock,
    ]
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual({
      stockId: 1,
      remainingQuantity: '10',
      bookingsQuantity: '20',
      quantity: 40,
      bookingLimitDatetime: new Date('2001-06-05T02:00:00.000Z'),
      price: 12,
      activationCodes: undefined,
      activationCodesExpirationDatetime: undefined,
    })
  })

  it('should normalize null values', () => {
    offer.stocks = [
      {
        nonHumanizedId: 1,
        bookingsQuantity: 20,
        quantity: null,
        bookingLimitDatetime: null,
        price: 12,
      } as IOfferIndividualStock,
    ]
    const initialValues = buildInitialValues(offer)
    expect(initialValues).toEqual({
      activationCodes: undefined,
      activationCodesExpirationDatetime: undefined,
      stockId: 1,
      remainingQuantity: 'unlimited',
      bookingsQuantity: '20',
      quantity: null,
      bookingLimitDatetime: null,
      price: 12,
    })
  })
})
