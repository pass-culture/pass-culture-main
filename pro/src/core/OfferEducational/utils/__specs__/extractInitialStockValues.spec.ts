import { GetCollectiveOfferCollectiveStockResponseModel } from 'apiClient/v1'
import { DEFAULT_EAC_STOCK_FORM_VALUES } from 'core/OfferEducational/constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational/types'

import { extractInitialStockValues } from '../extractInitialStockValues'

describe('extractInitialVisibilityValues', () => {
  it('should return default values when collectiveStock is not defined', () => {
    expect(
      extractInitialStockValues({ collectiveStock: null } as CollectiveOffer)
    ).toStrictEqual(DEFAULT_EAC_STOCK_FORM_VALUES)
  })

  it('should return stock details', () => {
    const stockValues: GetCollectiveOfferCollectiveStockResponseModel = {
      beginningDatetime: '2023-02-23T10:46:20Z',
      bookingLimitDatetime: '2023-02-28T10:46:20Z',
      educationalPriceDetail: 'test',
      id: 'UM',
      nonHumanizedId: 1,
      isBooked: false,
      isCancellable: false,
      isEducationalStockEditable: true,
      numberOfTickets: 20,
      price: 1200,
    }
    expect(
      extractInitialStockValues({
        venue: { departementCode: '75' },
        collectiveStock: stockValues,
      } as CollectiveOffer)
    ).toStrictEqual({
      bookingLimitDatetime: new Date('2023-02-28T11:46:20.000Z'),
      eventDate: new Date('2023-02-23T11:46:20.000Z'),
      eventTime: new Date('2023-02-23T11:46:20.000Z'),
      educationalOfferType: 'CLASSIC',
      numberOfPlaces: 20,
      priceDetail: 'test',
      totalPrice: 1200,
    })
  })

  it('should return default values with educationPriceDetail when educationalPriceDetail is defined', () => {
    expect(
      extractInitialStockValues(
        { collectiveStock: null } as CollectiveOffer,
        {
          educationalPriceDetail: 'initialStockValues',
        } as CollectiveOfferTemplate
      )
    ).toStrictEqual({
      ...DEFAULT_EAC_STOCK_FORM_VALUES,
      priceDetail: 'initialStockValues',
    })
  })
})
