import { OfferStatus } from '@/apiClient//v1'

import { computeIndividualOffersUrl } from '../computeIndividualOffersUrl'

describe('computeIndividualOffersUrl', () => {
  it('should return simple query for offers page when no search filters', () => {
    const offersSearchFilters = {}

    const value = computeIndividualOffersUrl(offersSearchFilters)

    expect(value).toBe('/offres')
  })

  it('should build proper query given offers filters', () => {
    const offersSearchFilters = {
      name: 'test',
      offererId: 'AY',
      venueId: 'EQ',
      categoryId: 'CINEMA',
      status: OfferStatus.ACTIVE,
      creationMode: 'manual',
      periodBeginningDate: '2020-11-30T00:00:00+01:00',
      periodEndingDate: '2021-01-07T23:59:59+01:00',
      page: 2,
    }

    const value = computeIndividualOffersUrl(offersSearchFilters)

    expect(value).toBe(
      '/offres?page=2&nom=test&structure=AY&lieu=EQ&categorie=CINEMA&statut=active&creation=manuelle&periode-evenement-debut=2020-11-30T00%3A00%3A00%2B01%3A00&periode-evenement-fin=2021-01-07T23%3A59%3A59%2B01%3A00'
    )
  })
})
