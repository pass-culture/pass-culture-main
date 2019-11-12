import { DEFAULT_MAX_DISTANCE } from '../../../components/pages/search/helpers'
import { selectRecommendations, selectRecommendationsBySearchQuery } from '../recommendationsSelectors'
import state from '../../../mocks/state'

const types = state.data.types

describe('selectRecommendationsBySearchQuery', () => {
  it('should select only recommendations from a specific search', () => {
    // given
    const currentSearchRecommendations = [
      {
        id: 'AE',
        productOrTutoIdentifier: 'product_GU',
        search: 'keywords_string=mimi',
      },
      {
        id: 'BF',
        productOrTutoIdentifier: 'product_GV',
        search: 'keywords_string=mimi&page=13',
      },
    ]
    const oldSearchRecommendations = [
      {
        id: 'CG',
        productOrTutoIdentifier: 'product_GL',
        search: 'keywords_string=toto',
      },
      {
        id: 'DH',
        productOrTutoIdentifier: 'product_GM',
        search: 'keywords_string=toto',
      },
    ]
    const fromDiscoveryRecommendations = [
      {
        id: 'HK',
        productOrTutoIdentifier: 'product_GZ',
        search: null,
      },
    ]
    const state = {
      data: {
        recommendations: [
          ...currentSearchRecommendations,
          ...fromDiscoveryRecommendations,
          ...oldSearchRecommendations,
        ],
        types,
      },
    }
    const location = {
      search: 'mots-cles=mimi',
    }

    // when
    const recommendations = selectRecommendationsBySearchQuery(state, location)

    // then
    expect(recommendations).toStrictEqual(currentSearchRecommendations)
  })

  it('should select recommendations from a search combining keywords and category', () => {
    // given
    const currentSearchedRecommendations = [
      {
        id: 'AE',
        productOrTutoIdentifier: 'product_GU',
        search:
          'keywords_string=narval&page=1&type_values=[\'EventType.MUSIQUE\', \'ThingType.MUSIQUE_ABO\', \'ThingType.MUSIQUE\']',
      },
      {
        id: 'BF',
        productOrTutoIdentifier: 'product_GV',
        search:
          'keywords_string=narval&page=12&type_values=[\'EventType.MUSIQUE\', \'ThingType.MUSIQUE_ABO\', \'ThingType.MUSIQUE\']',
      },
    ]
    const state = {
      data: {
        recommendations: [...currentSearchedRecommendations],
        types,
      },
    }
    const location = {
      search: 'mots-cles=narval&page=12&categories=Écouter',
    }

    // when
    const recommendations = selectRecommendationsBySearchQuery(state, location)

    // then
    expect(recommendations).toStrictEqual(currentSearchedRecommendations)
  })

  it('should select recommendations from a category search', () => {
    // given
    const currentSearchedRecommendations = [
      {
        id: 'AE',
        productOrTutoIdentifier: 'product_GU',
        search:
          'page=2&type_values=[\'ThingType.LIVRE_EDITION\', \'ThingType.LIVRE_AUDIO\', \'ThingType.PRESSE_ABO\']',
      },
      {
        id: 'BF',
        productOrTutoIdentifier: 'product_GV',
        search:
          'page=251&type_values=[\'ThingType.LIVRE_EDITION\', \'ThingType.LIVRE_AUDIO\', \'ThingType.PRESSE_ABO\']',
      },
      {
        id: 'BF',
        productOrTutoIdentifier: 'product_GT',
        search:
          'type_values=[\'ThingType.LIVRE_EDITION\', \'ThingType.LIVRE_AUDIO\', \'ThingType.PRESSE_ABO\']',
      },
    ]

    const state = {
      data: {
        recommendations: [...currentSearchedRecommendations],
        types,
      },
    }

    const location = {
      search: '?categories=Lire',
    }

    // when
    const recommendations = selectRecommendationsBySearchQuery(state, location)

    // then
    expect(recommendations).toStrictEqual(currentSearchedRecommendations)
  })

  it('should select recommendations from a distance less than 10 km search', () => {
    // given
    const currentSearchedRecommendations = [
      {
        id: 'AE',
        productOrTutoIdentifier: 'product_GU',
        search:
          'latitude=48.86&longitude=2.34&max_distance=50.0&page=1&type_values=[\'EventType.SPECTACLE_VIVANT\', \'ThingType.SPECTACLE_VIVANT_ABO\']',
      },
      {
        id: 'BF',
        productOrTutoIdentifier: 'product_GV',
        search:
          'latitude=48.86&longitude=2.34&max_distance=50.0&type_values=[\'EventType.SPECTACLE_VIVANT\', \'ThingType.SPECTACLE_VIVANT_ABO\']',
      },
    ]

    const state = {
      data: {
        recommendations: [...currentSearchedRecommendations],
        types,
      },
    }

    const location = {
      search: '?categories=Applaudir&distance=50&latitude=48.86&longitude=2.34',
    }

    // when
    const recommendations = selectRecommendationsBySearchQuery(state, location)

    // then
    expect(recommendations).toStrictEqual(currentSearchedRecommendations)
  })

  it('should select recommendations without filter on distance', () => {
    // given
    const currentSearchedRecommendations = [
      {
        id: 'AE',
        productOrTutoIdentifier: 'product_GU',
        search:
          'page=1&type_values=[\'EventType.SPECTACLE_VIVANT\', \'ThingType.SPECTACLE_VIVANT_ABO\']',
      },
      {
        id: 'BF',
        productOrTutoIdentifier: 'product_GV',
        search: 'type_values=[\'EventType.SPECTACLE_VIVANT\', \'ThingType.SPECTACLE_VIVANT_ABO\']',
      },
    ]

    const state = {
      data: {
        recommendations: [...currentSearchedRecommendations],
        types,
      },
    }

    const location = {
      search: `?categories=Applaudir&distance=${DEFAULT_MAX_DISTANCE}&latitude=48.86320299867651&longitude=2.343763285384099`,
    }

    // when
    const recommendations = selectRecommendationsBySearchQuery(state, location)

    // then
    expect(recommendations).toStrictEqual(currentSearchedRecommendations)
  })

  it('should retrieve recommendation with "?" in search', () => {
    // given
    const state = {
      data: {
        recommendations: [
          {
            id: 'AE',
            search: 'keywords_string=MENSCH ! SONT LES HOMMES ?&page=1',
          },
        ],
      },
    }

    const location = {
      search: 'mots-cles=MENSCH ! SONT LES HOMMES %3F&page=1',
    }

    // when
    const recommendations = selectRecommendationsBySearchQuery(state, location)

    // then
    expect(recommendations).toStrictEqual([
      {
        id: 'AE',
        search: 'keywords_string=MENSCH ! SONT LES HOMMES ?&page=1',
      },
    ])
  })
})

describe('selectRecommendations', () => {
  it('should return recommendations', () => {
    // given
    const state = {
      data: {
        recommendations: [{ id: 'AEY1' }]
      }
    }

    // when
    const result = selectRecommendations(state)

    // then
    expect(result).toStrictEqual([{ id: 'AEY1' }])
  })
})



