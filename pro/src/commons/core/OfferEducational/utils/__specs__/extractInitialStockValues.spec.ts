import type { GetCollectiveOfferCollectiveStockResponseModel } from '@/apiClient/v1/new'
import {
  defaultGetCollectiveOfferRequest,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'

import type { CollectiveOfferStockFormValues } from '../../types'
import { extractInitialStockValues } from '../extractInitialStockValues'

const emptyCollectiveStockFormValues: CollectiveOfferStockFormValues = {
  startDate: '',
  endDate: '',
  eventTime: '',
  numberOfTickets: null,
  totalPrice: null,
  bookingLimitDate: '',
  educationalPriceDetail: '',
}

describe('extractInitialStockValues', () => {
  it('should return default values when collectiveStock is not defined', () => {
    expect(
      extractInitialStockValues(
        getCollectiveOfferFactory({
          collectiveStock: null,
        })
      )
    ).toStrictEqual(emptyCollectiveStockFormValues)
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
      numberOfTickets: 20,
      educationalPriceDetail: 'test',
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
      ...emptyCollectiveStockFormValues,
      educationalPriceDetail: 'initialStockValues',
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
      ...emptyCollectiveStockFormValues,
      startDate: '2030-07-30',
      numberOfTickets: 20,
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
    ).toStrictEqual(emptyCollectiveStockFormValues)
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
    ).toStrictEqual({ ...emptyCollectiveStockFormValues, numberOfTickets: 8 })
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
    ).toStrictEqual({ ...emptyCollectiveStockFormValues, numberOfTickets: 6 })
  })
})
