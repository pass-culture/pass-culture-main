import { OfferStatus } from 'apiClient/v1'
import {
  OfferIndividual,
  OfferIndividualVenueProvider,
} from 'core/Offers/types'

import { StockThingFormValues } from '../..'
import setFormReadOnlyFields from '../setFormReadOnlyFields'

describe('StockThingForm::utils::setFormReadOnlyFields', () => {
  let offer: OfferIndividual
  let currentStock: StockThingFormValues
  beforeEach(() => {
    offer = {} as OfferIndividual
    currentStock = {} as StockThingFormValues
  })
  const disabledStatus = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(disabledStatus)(
    'should disabled field for disable statuts "%s"',
    (status: OfferStatus) => {
      offer.status = status
      const readOnlyFields = setFormReadOnlyFields(offer, currentStock)
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
    } as OfferIndividualVenueProvider
    const readOnlyFields = setFormReadOnlyFields(offer, currentStock)
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
    offer.lastProvider = { name: 'allociné' } as OfferIndividualVenueProvider
    currentStock = {
      activationCodes: new Array<string>(),
    } as StockThingFormValues
    const readOnlyFields = setFormReadOnlyFields(offer, currentStock)
    expect(readOnlyFields).toEqual([])
  })
})
