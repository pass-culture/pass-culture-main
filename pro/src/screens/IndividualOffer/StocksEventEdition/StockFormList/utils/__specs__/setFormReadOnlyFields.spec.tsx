import { OfferStatus } from 'apiClient/v1'

import setFormReadOnlyFields from '../setFormReadOnlyFields'

describe('setFormReadOnlyFields', () => {
  it('should return empty array when offer is draft', () => {
    const aLongTimeAgo = new Date('2021-01-01')
    const today = new Date()
    const readOnlyFields = setFormReadOnlyFields({
      beginningDate: aLongTimeAgo,
      today,
      lastProviderName: '',
      offerStatus: OfferStatus.DRAFT,
    })
    expect(readOnlyFields).toStrictEqual([])
  })

  it('should return full array when offer is pending', () => {
    const aLongTimeAgo = new Date('2021-01-01')
    const today = new Date()
    const readOnlyFields = setFormReadOnlyFields({
      beginningDate: aLongTimeAgo,
      today,
      lastProviderName: '',
      offerStatus: OfferStatus.PENDING,
    })
    expect(readOnlyFields).toStrictEqual([
      'beginningDate',
      'beginningTime',
      'remainingQuantity',
      'bookingsQuantity',
      'bookingLimitDatetime',
      'priceCategoryId',
      'stockId',
      'isDeletable',
      'readOnlyFields',
    ])
  })

  it('should return full array when offer is pending', () => {
    const aLongTimeAgo = new Date('2021-01-01')
    const today = new Date()
    const readOnlyFields = setFormReadOnlyFields({
      beginningDate: aLongTimeAgo,
      today,
      lastProviderName: '',
      offerStatus: OfferStatus.REJECTED,
    })
    expect(readOnlyFields).toStrictEqual([
      'beginningDate',
      'beginningTime',
      'remainingQuantity',
      'bookingsQuantity',
      'bookingLimitDatetime',
      'priceCategoryId',
      'stockId',
      'isDeletable',
      'readOnlyFields',
    ])
  })

  it('should return full array when offer is from provider', () => {
    const aLongTimeAgo = new Date('2021-01-01')
    const today = new Date()
    const readOnlyFields = setFormReadOnlyFields({
      beginningDate: aLongTimeAgo,
      today,
      lastProviderName: 'provider',
      offerStatus: OfferStatus.ACTIVE,
    })
    expect(readOnlyFields).toStrictEqual([
      'beginningDate',
      'beginningTime',
      'remainingQuantity',
      'bookingsQuantity',
      'bookingLimitDatetime',
      'priceCategoryId',
      'stockId',
      'isDeletable',
      'readOnlyFields',
    ])
  })

  it('should return array when offer is allociné', () => {
    const today = new Date()
    const readOnlyFields = setFormReadOnlyFields({
      beginningDate: null,
      today,
      lastProviderName: 'allociné',
      offerStatus: OfferStatus.ACTIVE,
    })
    expect(readOnlyFields).toStrictEqual(['beginningDate', 'beginningTime'])
  })

  it('should return array when offer is from other cinema provider like boost', () => {
    const today = new Date()
    const readOnlyFields = setFormReadOnlyFields({
      beginningDate: null,
      today,
      lastProviderName: 'boost',
      offerStatus: OfferStatus.ACTIVE,
    })
    expect(readOnlyFields).toStrictEqual([
      'beginningDate',
      'beginningTime',
      'priceCategoryId',
    ])
  })
})
