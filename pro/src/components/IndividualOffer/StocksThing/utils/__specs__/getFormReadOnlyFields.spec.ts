import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'commons/utils/factories/individualApiFactories'

import { StockThingFormValues } from '../../types'
import { getFormReadOnlyFields } from '../getFormReadOnlyFields'

describe('StockThingForm::utils::getFormReadOnlyFields', () => {
  let offer: GetIndividualOfferResponseModel
  let currentStock: StockThingFormValues
  beforeEach(() => {
    offer = getIndividualOfferFactory()
    currentStock = {} as StockThingFormValues
  })
  const disabledStatus = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(disabledStatus)(
    'should disabled field for disable statuts "%s"',
    (status: OfferStatus) => {
      offer.status = status
      const readOnlyFields = getFormReadOnlyFields(
        offer,
        [getOfferStockFactory()],
        currentStock
      )
      expect(readOnlyFields).toEqual([
        'stockId',
        'remainingQuantity',
        'bookingsQuantity',
        'bookingLimitDatetime',
        'quantity',
        'price',
        'activationCodes',
        'activationCodesExpirationDatetime',
        'isDuo',
      ])
    }
  )

  it('should disabled field synchronized offer', () => {
    offer.lastProvider = {
      name: 'any provider',
    }
    const readOnlyFields = getFormReadOnlyFields(
      offer,
      [getOfferStockFactory()],
      currentStock
    )
    expect(readOnlyFields).toEqual([
      'stockId',
      'remainingQuantity',
      'bookingsQuantity',
      'bookingLimitDatetime',
      'quantity',
      'price',
      'activationCodes',
      'activationCodesExpirationDatetime',
      'isDuo',
    ])
  })

  it('should not disabled field for allociné synchronized offer', () => {
    offer.lastProvider = { name: 'allociné' }
    currentStock = {
      activationCodes: new Array<string>(),
    } as StockThingFormValues
    const readOnlyFields = getFormReadOnlyFields(
      offer,
      [getOfferStockFactory()],
      currentStock
    )
    expect(readOnlyFields).toEqual([])
  })
})
