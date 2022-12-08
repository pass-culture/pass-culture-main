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
})
