import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from 'utils/individualApiFactories'

import { StockThingFormValues } from '../../types'
import { setFormReadOnlyFields } from '../setFormReadOnlyFields'

describe('StockThingForm::utils::setFormReadOnlyFields', () => {
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
      const readOnlyFields = setFormReadOnlyFields(
        offer,
        [getOfferStockFactory()],
        currentStock
      )
      expect(readOnlyFields).toEqual([
        'stockId',
        'remainingQuantity',
        'bookingsQuantity',
        'quantity',
        'bookingLimitDatetime',
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
    const readOnlyFields = setFormReadOnlyFields(
      offer,
      [getOfferStockFactory()],
      currentStock
    )
    expect(readOnlyFields).toEqual([
      'stockId',
      'remainingQuantity',
      'bookingsQuantity',
      'quantity',
      'bookingLimitDatetime',
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
    const readOnlyFields = setFormReadOnlyFields(
      offer,
      [getOfferStockFactory()],
      currentStock
    )
    expect(readOnlyFields).toEqual([])
  })
})
