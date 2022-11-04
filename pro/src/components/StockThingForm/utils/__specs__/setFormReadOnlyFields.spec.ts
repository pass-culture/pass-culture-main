import { OfferStatus } from 'apiClient/v1'
import {
  IOfferIndividual,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'

import setFormReadOnlyFields from '../setFormReadOnlyFields'

describe('StockThingForm::utils::setFormReadOnlyFields', () => {
  let offer: IOfferIndividual
  beforeEach(() => {
    offer = {} as IOfferIndividual
  })
  const disabledStatus = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(disabledStatus)(
    'should disabled field for disable statuts "%s"',
    (status: OfferStatus) => {
      offer.status = status
      const readOnlyFields = setFormReadOnlyFields(offer)
      expect(readOnlyFields).toEqual([
        'stockId',
        'remainingQuantity',
        'bookingsQuantity',
        'quantity',
        'bookingLimitDatetime',
        'price',
      ])
    }
  )

  it('should disabled field synchronized offer', () => {
    offer.lastProvider = {
      name: 'any provider',
    } as IOfferIndividualVenueProvider
    const readOnlyFields = setFormReadOnlyFields(offer)
    expect(readOnlyFields).toEqual([
      'stockId',
      'remainingQuantity',
      'bookingsQuantity',
      'quantity',
      'bookingLimitDatetime',
      'price',
    ])
  })

  it('should not disabled field for allociné synchronized offer', () => {
    offer.lastProvider = { name: 'allociné' } as IOfferIndividualVenueProvider
    const readOnlyFields = setFormReadOnlyFields(offer)
    expect(readOnlyFields).toEqual([])
  })
})
