import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  OfferStatus,
} from '@/apiClient//v1'
import { Audience } from '@/commons/core/shared/types'
import {
  translateApiParamsToQueryParams,
  translateQueryParamsToApiParams,
} from '@/commons/utils/translate'

describe('translate', () => {
  it('should translate between query params to api params for collective offers', () => {
    expect(
      translateQueryParamsToApiParams(
        {
          'nom-ou-isbn': 'input de recherche',
          structure: '883',
          lieu: '891',
          format: 'Concert',
          'periode-evenement-debut': '2024-08-08',
          'periode-evenement-fin': '2024-08-24',
          statut: ['en-attente', 'active'],
        },
        Audience.COLLECTIVE
      )
    ).toEqual(
      expect.objectContaining({
        nameOrIsbn: 'input de recherche',
        offererId: '883',
        venueId: '891',
        format: 'Concert',
        periodBeginningDate: '2024-08-08',
        periodEndingDate: '2024-08-24',
        status: ['UNDER_REVIEW', 'PUBLISHED'],
      })
    )

    expect(
      translateApiParamsToQueryParams(
        {
          nameOrIsbn: 'input de recherche',
          offererId: '883',
          venueId: '891',
          format: EacFormat.CONCERT,
          periodBeginningDate: '2024-08-08',
          periodEndingDate: '2024-08-24',
          status: [
            CollectiveOfferDisplayedStatus.UNDER_REVIEW,
            CollectiveOfferDisplayedStatus.PUBLISHED,
          ],
        },
        Audience.COLLECTIVE
      )
    ).toEqual(
      expect.objectContaining({
        'nom-ou-isbn': 'input de recherche',
        structure: '883',
        lieu: '891',
        format: 'Concert',
        'periode-evenement-debut': '2024-08-08',
        'periode-evenement-fin': '2024-08-24',
        statut: ['en-attente', 'active'],
      })
    )
  })

  it('should translate query params to api params for individual offers', () => {
    expect(
      translateQueryParamsToApiParams(
        {
          'nom-ou-isbn': 'input de recherche',
          structure: '883',
          lieu: '891',
          'periode-evenement-debut': '2024-08-08',
          'periode-evenement-fin': '2024-08-24',
          statut: 'draft',
        },
        Audience.INDIVIDUAL
      )
    ).toEqual(
      expect.objectContaining({
        nameOrIsbn: 'input de recherche',
        offererId: '883',
        venueId: '891',
        periodBeginningDate: '2024-08-08',
        periodEndingDate: '2024-08-24',
        status: 'DRAFT',
      })
    )

    expect(
      translateApiParamsToQueryParams(
        {
          nameOrIsbn: 'input de recherche',
          offererId: '883',
          venueId: '891',
          periodBeginningDate: '2024-08-08',
          periodEndingDate: '2024-08-24',
          status: OfferStatus.DRAFT,
        },
        Audience.INDIVIDUAL
      )
    ).toEqual(
      expect.objectContaining({
        'nom-ou-isbn': 'input de recherche',
        structure: '883',
        lieu: '891',
        'periode-evenement-debut': '2024-08-08',
        'periode-evenement-fin': '2024-08-24',
        statut: 'draft',
      })
    )
  })

  it('should not translate user inputs for collective offers', () => {
    expect(
      translateQueryParamsToApiParams(
        {
          'nom-ou-isbn': 'en-attente',
        },
        Audience.COLLECTIVE
      )
    ).toEqual(expect.objectContaining({ nameOrIsbn: 'en-attente' }))
  })

  it('should not translate user inputs for individual offers', () => {
    expect(
      translateQueryParamsToApiParams(
        {
          'nom-ou-isbn': 'remboursements',
        },
        Audience.INDIVIDUAL
      )
    ).toEqual(expect.objectContaining({ nameOrIsbn: 'remboursements' }))
  })
})
