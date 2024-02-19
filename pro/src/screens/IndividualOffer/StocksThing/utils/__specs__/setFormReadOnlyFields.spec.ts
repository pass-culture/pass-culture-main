import { OfferStatus } from 'apiClient/v1'
import { IndividualOffer } from 'core/Offers/types'
import { GetIndividualOfferFactory } from 'utils/apiFactories'
import { individualGetOfferStockResponseModelFactory } from 'utils/individualApiFactories'

import { StockThingFormValues } from '../../types'
import setFormReadOnlyFields from '../setFormReadOnlyFields'

describe('StockThingForm::utils::setFormReadOnlyFields', () => {
  let offer: IndividualOffer
  let currentStock: StockThingFormValues
  beforeEach(() => {
    offer = GetIndividualOfferFactory()
    currentStock = {} as StockThingFormValues
  })
  const disabledStatus = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(disabledStatus)(
    'should disabled field for disable statuts "%s"',
    (status: OfferStatus) => {
      offer.status = status
      const readOnlyFields = setFormReadOnlyFields(
        offer,
        [individualGetOfferStockResponseModelFactory()],
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
      [individualGetOfferStockResponseModelFactory()],
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
      [individualGetOfferStockResponseModelFactory()],
      currentStock
    )
    expect(readOnlyFields).toEqual([])
  })
})
