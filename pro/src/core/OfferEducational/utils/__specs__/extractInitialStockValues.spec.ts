import { GetCollectiveOfferCollectiveStockResponseModel } from 'apiClient/v1'
import { DEFAULT_EAC_STOCK_FORM_VALUES } from 'core/OfferEducational/constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational/types'
import { defaultRequestResponseModel } from 'utils/collectiveApiFactories'

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

  it('should return stock details from requested offer when requestedDate, totalStudents and totalTeachers are defined', () => {
    expect(
      extractInitialStockValues(
        {
          venue: { departementCode: '75' },
        } as CollectiveOffer,
        {
          educationalPriceDetail: 'initialStockValues',
        } as CollectiveOfferTemplate,
        {
          ...defaultRequestResponseModel,
          requestedDate: '2030-07-30',
          totalStudents: 10,
          totalTeachers: 10,
        }
      )
    ).toStrictEqual({
      bookingLimitDatetime: null,
      eventDate: new Date('2030-07-30T00:00:00.000Z'),
      eventTime: '',
      educationalOfferType: 'CLASSIC',
      numberOfPlaces: 20,
      priceDetail: '',
      totalPrice: '',
    })
  })

  it('should return stock details from requested offer when requestedDate, totalStudents and totalTeachers are not defined', () => {
    expect(
      extractInitialStockValues(
        {
          venue: { departementCode: '75' },
        } as CollectiveOffer,
        {
          educationalPriceDetail: 'initialStockValues',
        } as CollectiveOfferTemplate,
        {
          ...defaultRequestResponseModel,
          requestedDate: null,
          totalStudents: null,
          totalTeachers: null,
        }
      )
    ).toStrictEqual({
      bookingLimitDatetime: null,
      eventDate: '',
      eventTime: '',
      educationalOfferType: 'CLASSIC',
      numberOfPlaces: '',
      priceDetail: '',
      totalPrice: '',
    })
  })

  it('should return stock details from requested offer when only totalStudents is defined', () => {
    expect(
      extractInitialStockValues(
        {
          venue: { departementCode: '75' },
        } as CollectiveOffer,
        {
          educationalPriceDetail: 'initialStockValues',
        } as CollectiveOfferTemplate,
        {
          ...defaultRequestResponseModel,
          totalStudents: 8,
        }
      )
    ).toStrictEqual({
      bookingLimitDatetime: null,
      eventDate: '',
      eventTime: '',
      educationalOfferType: 'CLASSIC',
      numberOfPlaces: 8,
      priceDetail: '',
      totalPrice: '',
    })
  })

  it('should return stock details from requested offer when only totalTeachers is defined', () => {
    expect(
      extractInitialStockValues(
        {
          venue: { departementCode: '75' },
        } as CollectiveOffer,
        {
          educationalPriceDetail: 'initialStockValues',
        } as CollectiveOfferTemplate,
        {
          ...defaultRequestResponseModel,
          totalTeachers: 6,
        }
      )
    ).toStrictEqual({
      bookingLimitDatetime: null,
      eventDate: '',
      eventTime: '',
      educationalOfferType: 'CLASSIC',
      numberOfPlaces: 6,
      priceDetail: '',
      totalPrice: '',
    })
  })
})
