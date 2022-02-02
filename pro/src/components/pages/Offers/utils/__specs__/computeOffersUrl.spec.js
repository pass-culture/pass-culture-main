import { computeOffersUrl } from '../computeOffersUrl'

describe('src | components | pages | Offer | utils | computeOffersUrl', () => {
  it('should return simple query for offers page when no search filters', () => {
    // given
    const offersSearchFilters = {}

    // when
    const value = computeOffersUrl(offersSearchFilters)

    // then
    expect(value).toBe('/offres')
  })

  it('should build proper query given offers filters', () => {
    // given
    const offersSearchFilters = {
      name: 'test',
      offererId: 'AY',
      venueId: 'EQ',
      categoryId: 'CINEMA',
      status: 'ACTIVE',
      creationMode: 'manual',
      periodBeginningDate: '2020-11-30T00:00:00+01:00',
      periodEndingDate: '2021-01-07T23:59:59+01:00',
      page: 1,
    }

    // when
    const value = computeOffersUrl(offersSearchFilters)

    // then
    expect(value).toBe(
      '/offres?nom=test&structure=AY&lieu=EQ&categorie=CINEMA&statut=active&creation=manuelle&periode-evenement-debut=2020-11-30T00%3A00%3A00%2B01%3A00&periode-evenement-fin=2021-01-07T23%3A59%3A59%2B01%3A00&page=1'
    )
  })
})
