import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { STOCK_THING_FORM_DEFAULT_VALUES } from 'components/StockThingForm'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import upsertStocksThingAdapter from '../upsertStocksThingAdapter'

describe('screens::StockThing::adapter:upsertStocksThingAdapter', () => {
  it('should send StockCreationBodyModel to api', async () => {
    jest
      .spyOn(api, 'upsertStocks')
      .mockResolvedValue({ stockIds: [{ id: 'Created_STOCK_ID' }] })
    upsertStocksThingAdapter({
      offerId: 'OFFER_ID',
      formValues: {
        activationCodesExpirationDatetime: null,
        activationCodes: [],
        remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: null,
        quantity: '12',
        price: '10',
      },
      departementCode: '75',
      mode: OFFER_WIZARD_MODE.CREATION,
    })
    expect(api.upsertStocks).toHaveBeenCalledWith({
      humanizedOfferId: 'OFFER_ID',
      stocks: [
        {
          bookingLimitDatetime: null,
          price: 10,
          quantity: 12,
        },
      ],
    })
  })
  it('should send StockEditionBodyModel to api', async () => {
    jest
      .spyOn(api, 'upsertStocks')
      .mockResolvedValue({ stockIds: [{ id: 'Created_STOCK_ID' }] })
    upsertStocksThingAdapter({
      offerId: 'OFFER_ID',
      formValues: {
        activationCodesExpirationDatetime: null,
        activationCodes: [],
        stockId: 'STOCK_ID',
        remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: null,
        quantity: '12',
        price: '10',
      },
      departementCode: '75',
      mode: OFFER_WIZARD_MODE.CREATION,
    })
    expect(api.upsertStocks).toHaveBeenCalledWith({
      humanizedOfferId: 'OFFER_ID',
      stocks: [
        {
          humanizedId: 'STOCK_ID',
          bookingLimitDatetime: null,
          price: 10,
          quantity: 12,
        },
      ],
    })
  })

  it('should return errors from api', async () => {
    jest.spyOn(api, 'upsertStocks').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            price: 'API price ERROR',
            quantity: 'API quantity ERROR',
            bookingLimitDatetime: 'API bookingLimitDatetime ERROR',
          },
        } as ApiResult,
        ''
      )
    )
    const reponse = await upsertStocksThingAdapter({
      offerId: 'OFFER_ID',
      formValues: {
        stockId: 'STOCK_ID',
        activationCodesExpirationDatetime: null,
        activationCodes: [],
        remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: null,
        quantity: '12',
        price: '10',
      },
      mode: OFFER_WIZARD_MODE.CREATION,
      departementCode: '75',
    })

    expect(reponse.payload).toEqual({
      errors: {
        price: 'API price ERROR',
        quantity: 'API quantity ERROR',
        bookingLimitDatetime: 'API bookingLimitDatetime ERROR',
      },
    })
  })
})
