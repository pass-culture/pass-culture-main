import { api } from 'apiClient/api'
import { ApiError, StockResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../'
import upsertStocksThingAdapter from '../upsertStocksThingAdapter'

describe('screens::StockThing::adapter:upsertStocksThingAdapter', () => {
  it('should send StockCreationBodyModel to api', async () => {
    jest
      .spyOn(api, 'upsertStocks')
      .mockResolvedValue({ stocks: [{ id: 'STOCK_ID' } as StockResponseModel] })
    upsertStocksThingAdapter({
      offerId: 1,
      formValues: {
        activationCodesExpirationDatetime: null,
        activationCodes: [],
        remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: null,
        quantity: 12,
        price: 10,
        isDuo: undefined,
      },
      departementCode: '75',
      mode: OFFER_WIZARD_MODE.CREATION,
    })
    expect(api.upsertStocks).toHaveBeenCalledWith({
      offerId: 1,
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
      .mockResolvedValue({ stocks: [{ id: 'STOCK_ID' } as StockResponseModel] })
    upsertStocksThingAdapter({
      offerId: 1,
      formValues: {
        activationCodesExpirationDatetime: null,
        activationCodes: [],
        stockId: 1,
        remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: null,
        quantity: 12,
        price: 10,
        isDuo: undefined,
      },
      departementCode: '75',
      mode: OFFER_WIZARD_MODE.CREATION,
    })
    expect(api.upsertStocks).toHaveBeenCalledWith({
      offerId: 1,
      stocks: [
        {
          id: 1,
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
      offerId: 1,
      formValues: {
        stockId: 12,
        activationCodesExpirationDatetime: null,
        activationCodes: [],
        remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: null,
        quantity: 12,
        price: 10,
        isDuo: undefined,
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
