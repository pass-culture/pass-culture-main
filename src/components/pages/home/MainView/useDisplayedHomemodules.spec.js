import Offers from './domain/ValueObjects/Offers'
import { PANE_LAYOUT } from './domain/layout'
import { getModulesToDisplay } from './useDisplayedHomeModules.utils'
import BusinessPane from './domain/ValueObjects/BusinessPane'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import RecommendationPane from './domain/ValueObjects/RecommendationPane'

const algolia = {
  aroundRadius: null,
  beginningDatetime: null,
  categories: ['Cinéma', 'Cours, ateliers', 'Livres'],
  endingDatetime: null,
  hitsPerPage: 3,
  isDigital: false,
  isDuo: true,
  isFree: false,
  isEvent: true,
  isGeolocated: false,
  isThing: true,
  newestOnly: true,
  priceMax: 10,
  priceMin: 1,
  title: 'Mes paramètres Algolia',
}
let display = {
  activeOn: '2020-07-01T00:00+02:00',
  activeUntil: '2020-07-30T00:00+02:00',
  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
  minOffers: 1,
  title: 'Les offres près de chez toi!',
}
const offerOne = {
  objectID: 'NE',
  offer: {
    dates: [],
    id: 'NE',
    label: 'Cinéma',
    name: "Dansons jusqu'en 2030",
    priceMax: 33,
    priceMin: 33,
    thumbUrl: 'http://localhost/storage/thumbs/mediations/KQ',
  },
  venue: {
    name: 'Le Sous-sol',
  },
}
const offerTwo = {
  objectID: 'AE',
  offer: {
    dates: [],
    id: 'AE',
    label: 'Presse',
    name: 'Naruto',
    priceMax: 1,
    priceMin: 12,
    thumbUrl: 'http://localhost/storage/thumbs/mediations/PP',
  },
  venue: {
    name: 'Librairie Kléber',
  },
}

describe('getModulesToDisplay', () => {
  it('should display module Business', () => {
    const algoliaMapping = {}
    const module = new BusinessPane({ title: 'Title' })
    expect(getModulesToDisplay([module], algoliaMapping, [])).toHaveLength(1)
  })
  it('should display module Exclu', () => {
    const algoliaMapping = {}
    const module = new ExclusivityPane({ alt: 'alt', image: 'image', offerId: 'offerId' })
    expect(getModulesToDisplay([module], algoliaMapping, [])).toHaveLength(1)
  })
  it('should display module Offer if enough offers', () => {
    const algoliaMapping = {
      moduleId: { hits: [offerOne, offerTwo], nbHits: 2, parsedParameters: {} },
    }
    display.minOffers = 2
    const module = new Offers({ algolia, display, moduleId: 'moduleId' })
    expect(getModulesToDisplay([module], algoliaMapping, [])).toHaveLength(1)
  })

  it('should not display Offer when no hits', () => {
    const algoliaMapping = {
      moduleId: { hits: [], nbHits: 0, parsedParameters: {} },
    }
    const module = new Offers({ algolia, display, moduleId: 'moduleId' })
    expect(getModulesToDisplay([module], algoliaMapping, [])).toHaveLength(0)
  })

  it('should not display Offer when not enough offers to be displayed', () => {
    const algoliaMapping = {
      moduleId: { hits: [offerOne, offerTwo], nbHits: 2, parsedParameters: {} },
    }
    display.minOffers = 3
    const module = new Offers({ algolia, display, moduleId: 'moduleId' })
    expect(getModulesToDisplay([module], algoliaMapping, [])).toHaveLength(0)
  })

  it('should display Recommendation module only when enough offers', () => {
    display.minOffers = 3
    let module = new RecommendationPane({ display })
    expect(getModulesToDisplay([module], {}, [offerOne, offerTwo])).toHaveLength(0)

    display.minOffers = 2
    module = new RecommendationPane({ display })
    expect(getModulesToDisplay([module], {}, [offerOne, offerTwo])).toHaveLength(1)
  })
})
