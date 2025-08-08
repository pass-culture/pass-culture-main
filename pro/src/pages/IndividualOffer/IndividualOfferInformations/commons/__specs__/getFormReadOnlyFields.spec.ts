import { OfferStatus } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from '../constants'
import { getFormReadOnlyFields } from '../utils'

describe('getFormReadOnlyFields', () => {
  it('should return all fields as read only when offer is rejected', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.REJECTED,
    })

    const result = getFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    )
  })

  it('should return all fields as read only when offer is pending', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.PENDING,
    })

    const result = getFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    )
  })

  it('should return some fields as not read only when offer is synchronized', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Allocine' },
    })

    const result = getFormReadOnlyFields(offer)

    expect(result).not.toContain(['accessibility'])
  })
})
