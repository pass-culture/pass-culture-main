import { CollectiveOfferDisplayedStatus, EacFormat } from '@/apiClient//v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'

import { computeCollectiveOffersUrl } from '../computeCollectiveOffersUrl'

describe('computeCollectiveOffersUrl', () => {
  it('should build proper query given collective offers filters', () => {
    const offersSearchFilters = {
      name: 'test',
      offererId: 'AY',
      venueId: 'EQ',
      format: EacFormat.CONCERT,
      status: [
        CollectiveOfferDisplayedStatus.PUBLISHED,
        CollectiveOfferDisplayedStatus.EXPIRED,
      ],
      creationMode: 'manual',
      periodBeginningDate: '2020-11-30T00:00:00+01:00',
      periodEndingDate: '2021-01-07T23:59:59+01:00',
      page: 2,
    }

    const value = computeCollectiveOffersUrl(offersSearchFilters)

    expect(value).toBe(
      '/offres/collectives?page=2&nom=test&structure=AY&lieu=EQ&format=Concert&statut=active&statut=expiree&creation=manuelle&periode-evenement-debut=2020-11-30T00%3A00%3A00%2B01%3A00&periode-evenement-fin=2021-01-07T23%3A59%3A59%2B01%3A00'
    )
  })

  it('should build proper query given template collective offers filters', () => {
    const offersSearchFilters = {
      name: 'test',
      offererId: 'AY',
      venueId: 'EQ',
      format: EacFormat.CONCERT,
      status: [CollectiveOfferDisplayedStatus.PUBLISHED],
      creationMode: 'manual',
      periodBeginningDate: '2020-11-30T00:00:00+01:00',
      periodEndingDate: '2021-01-07T23:59:59+01:00',
      page: 2,
    }

    const value = computeCollectiveOffersUrl(
      offersSearchFilters,
      DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      true
    )

    expect(value).toBe(
      '/offres/vitrines?page=2&nom=test&structure=AY&lieu=EQ&format=Concert&statut=active&creation=manuelle&periode-evenement-debut=2020-11-30T00%3A00%3A00%2B01%3A00&periode-evenement-fin=2021-01-07T23%3A59%3A59%2B01%3A00'
    )
  })
})
