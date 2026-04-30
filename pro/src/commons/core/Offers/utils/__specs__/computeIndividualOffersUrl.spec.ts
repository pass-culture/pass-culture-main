import { OfferStatus } from '@/apiClient/v1'

import { computeIndividualOffersUrl } from '../computeIndividualOffersUrl'

describe('computeIndividualOffersUrl', () => {
  it('should return simple query for offers page when no search filters', () => {
    const offersSearchFilters = {}

    const value = computeIndividualOffersUrl(offersSearchFilters)

    expect(value).toBe('/offres')
  })

  it('should build proper query given offers filters', () => {
    const value = computeIndividualOffersUrl({
      nameOrIsbn: 'test',
      offererId: 42,
      venueId: 17,
      categoryId: 'CINEMA',
      status: OfferStatus.ACTIVE,
      creationMode: 'manual',
      periodBeginningDate: '2020-11-30T00:00:00+01:00',
      periodEndingDate: '2021-01-07T23:59:59+01:00',
      page: 2,
    })

    expect(value).toBe(
      '/offres?page=2&nom-ou-isbn=test&structure=42&lieu=17&categorie=CINEMA&statut=active&creation=manuelle&periode-evenement-debut=2020-11-30T00%3A00%3A00%2B01%3A00&periode-evenement-fin=2021-01-07T23%3A59%3A59%2B01%3A00'
    )
  })
})
