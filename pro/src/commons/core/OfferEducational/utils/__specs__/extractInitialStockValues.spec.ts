import type { GetCollectiveOfferCollectiveStockResponseModel } from '@/apiClient/v1/new'
import { DEFAULT_EAC_STOCK_FORM_VALUES } from '@/commons/core/OfferEducational/constants'
import {
  defaultGetCollectiveOfferRequest,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'

import { extractInitialStockValues } from '../extractInitialStockValues'

describe('extractInitialStockValues', () => {
  it('should return default values when collectiveStock is not defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          collectiveStock: null,
        })
      )
    ).toStrictEqual(DEFAULT_EAC_STOCK_FORM_VALUES)
  })

  it('should return stock details', () => {
    const stockValues: GetCollectiveOfferCollectiveStockResponseModel = {
      startDatetime: '2023-02-23T10:46:20Z',
      endDatetime: '2023-02-23T10:46:20Z',
      bookingLimitDatetime: '2023-02-28T10:46:20Z',
      educationalPriceDetail: 'test',
      id: 1,
      numberOfTickets: 20,
      price: 1200,
    }
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          venue: getCollectiveOfferVenueFactory({ departementCode: '75' }),
          collectiveStock: stockValues,
        })
      )
    ).toStrictEqual({
      bookingLimitDate: '2023-02-28',
      startDate: '2023-02-23',
      endDate: '2023-02-23',
      eventTime: '11:46',
      numberOfPlaces: 20,
      priceDetail: 'test',
      totalPrice: 1200,
    })
  })

  it('should return default values with educationPriceDetail when educationalPriceDetail is defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({ collectiveStock: null }),
        getCollectiveOfferTemplateFactory({
          educationalPriceDetail: 'initialStockValues',
        })
      )
    ).toStrictEqual({
      ...DEFAULT_EAC_STOCK_FORM_VALUES,
      priceDetail: 'initialStockValues',
    })
  })

  it('should return stock details from requested offer when requestedDate, totalStudents and totalTeachers are defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          venue: getCollectiveOfferVenueFactory({ departementCode: '75' }),
        }),
        getCollectiveOfferTemplateFactory({
          educationalPriceDetail: 'initialStockValues',
        }),
        {
          ...defaultGetCollectiveOfferRequest,
          requestedDate: '2030-07-30',
          totalStudents: 10,
          totalTeachers: 10,
        }
      )
    ).toStrictEqual({
      bookingLimitDate: '',
      startDate: '2030-07-30',
      endDate: '',
      eventTime: '',
      numberOfPlaces: 20,
      priceDetail: '',
      totalPrice: null,
    })
  })

  it('should return stock details from requested offer when requestedDate, totalStudents and totalTeachers are not defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          venue: getCollectiveOfferVenueFactory({ departementCode: '75' }),
        }),
        getCollectiveOfferTemplateFactory({
          educationalPriceDetail: 'initialStockValues',
        }),
        {
          ...defaultGetCollectiveOfferRequest,
          requestedDate: null,
          totalStudents: null,
          totalTeachers: null,
        }
      )
    ).toStrictEqual({
      bookingLimitDate: '',
      startDate: '',
      endDate: '',
      eventTime: '',
      numberOfPlaces: null,
      priceDetail: '',
      totalPrice: null,
    })
  })

  it('should return stock details from requested offer when only totalStudents is defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          venue: getCollectiveOfferVenueFactory({ departementCode: '75' }),
        }),
        getCollectiveOfferTemplateFactory({
          educationalPriceDetail: 'initialStockValues',
        }),
        {
          ...defaultGetCollectiveOfferRequest,
          totalStudents: 8,
        }
      )
    ).toStrictEqual({
      bookingLimitDate: '',
      startDate: '',
      endDate: '',
      eventTime: '',
      numberOfPlaces: 8,
      priceDetail: '',
      totalPrice: null,
    })
  })

  it('should return stock details from requested offer when only totalTeachers is defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          venue: getCollectiveOfferVenueFactory({ departementCode: '75' }),
        }),
        getCollectiveOfferTemplateFactory({
          educationalPriceDetail: 'initialStockValues',
        }),
        {
          ...defaultGetCollectiveOfferRequest,
          totalTeachers: 6,
        }
      )
    ).toStrictEqual({
      bookingLimitDate: '',
      startDate: '',
      endDate: '',
      eventTime: '',
      numberOfPlaces: 6,
      priceDetail: '',
      totalPrice: null,
    })
  })
})
