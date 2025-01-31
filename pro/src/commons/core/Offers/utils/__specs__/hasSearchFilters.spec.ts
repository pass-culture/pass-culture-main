import { EacFormat } from 'apiClient/adage'
import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'

import {
  CollectiveOfferTypeEnum,
  CollectiveSearchFiltersParams,
} from '../../types'
import { hasCollectiveSearchFilters } from '../hasSearchFilters'

describe('hasSearchFilters', () => {
  const defaultCollectiveFilters: CollectiveSearchFiltersParams = {
    collectiveOfferType: CollectiveOfferTypeEnum.ALL,
    format: 'all',
    nameOrIsbn: '',
    offererId: '333',
    page: 1,
    periodBeginningDate: '',
    periodEndingDate: '',
    status: [],
    venueId: '',
  }

  it('should confirm whether collective filters are applied or not', () => {
    expect(
      hasCollectiveSearchFilters(defaultCollectiveFilters, {
        ...defaultCollectiveFilters,
      })
    ).toBeFalsy()

    expect(
      hasCollectiveSearchFilters(defaultCollectiveFilters, {
        ...defaultCollectiveFilters,
        format: EacFormat.ATELIER_DE_PRATIQUE,
      })
    ).toBeTruthy()

    expect(
      hasCollectiveSearchFilters(defaultCollectiveFilters, {
        ...defaultCollectiveFilters,
        status: [CollectiveOfferDisplayedStatus.ACTIVE],
      })
    ).toBeTruthy()
  })

  it('should ignore the page number and offerer id', () => {
    expect(
      hasCollectiveSearchFilters(defaultCollectiveFilters, {
        ...defaultCollectiveFilters,
        page: 10,
      })
    ).toBeFalsy()

    expect(
      hasCollectiveSearchFilters(defaultCollectiveFilters, {
        ...defaultCollectiveFilters,
        offererId: '816',
      })
    ).toBeFalsy()
  })
})
