import filterIconByState, {
  descriptionForSublabel,
  getFirstChangingKey,
  handleQueryAdd,
  INITIAL_FILTER_PARAMS,
  isSearchFiltersAdded,
  searchResultsTitle,
} from '../utils'

describe('src | components | pages | search | utils', () => {
  describe('filterIconByState', () => {
    it('should render filter icon when there is no filter added to isSearchFiltersAdded', () => {
      expect(filterIconByState(true)).toEqual('filter')
    })
    it('should render filter-active icon when there is filters added to search', () => {
      expect(filterIconByState(false)).toEqual('filter-active')
    })
  })

  describe('isSearchFiltersAdded', () => {
    it('should return false if there is params changed with filter', () => {
      const queryParams = {
        categories: '%C3%89couter,Pratiquer',
        date: '2018-09-25T09:38:20.576Z',
        days: null,
        distance: null,
        jours: '0-1,1-5,5-100000',
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        page: '2',
        types: null,
      }
      expect(isSearchFiltersAdded(INITIAL_FILTER_PARAMS, queryParams)).toEqual(
        false
      )
    })

    it('should return true if there is no params changed with filter', () => {
      const queryParams = {
        categories: null,
        date: null,
        days: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        page: '2',
        types: null,
      }
      expect(isSearchFiltersAdded(INITIAL_FILTER_PARAMS, queryParams)).toEqual(
        true
      )
    })
  })

  describe('getFirstChangingKey', () => {
    it('should return the name of the key wich value has changed', () => {
      const nextObject = { jours: '0-1,1-5' }
      expect(getFirstChangingKey(INITIAL_FILTER_PARAMS, nextObject)).toEqual(
        'jours'
      )
    })
  })

  describe('searchResultsTitle', () => {
    it('should return the title corresponding to search result', () => {
      // given
      const keywords = 'fake word'
      const items = []
      const queryParams = {
        categories: null,
        date: null,
        days: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        page: '2',
        types: null,
      }

      expect(searchResultsTitle(keywords, items, queryParams)).toEqual(
        '"fake word" : 0 résultat'
      )
    })

    it('should return the title corresponding to search result', () => {
      // given
      const keywords = 'fake word'
      const items = []
      const queryParams = {
        categories: 'Lire',
        date: null,
        days: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        page: '2',
        types: null,
      }

      expect(searchResultsTitle(keywords, items, queryParams)).toEqual(
        '"fake word" : 0 résultat'
      )
    })

    it('should return the title corresponding to search result', () => {
      // given
      const keywords = 'fake word'
      const items = [{}, {}]
      const queryParams = {
        categories: 'Lire',
        date: null,
        days: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        page: '2',
        types: null,
      }

      expect(searchResultsTitle(keywords, items, queryParams)).toEqual(
        '"fake word" : 2 résultats'
      )
    })
  })

  describe('descriptionForSublabel', () => {
    it('should return the description corresponding to the label', () => {
      const typeSublabels = [
        {
          description:
            'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
          sublabel: 'Applaudir',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Jouer',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Lire',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Pratiquer',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Regarder',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Rencontrer',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Écouter',
        },
      ]
      const category = 'Applaudir'
      const result = descriptionForSublabel(category, typeSublabels)

      expect(result).toEqual(typeSublabels[0].description)
    })
  })
  describe.skip('handleQueryAdd', () => {
    // used in FilterByDates

    const currentState = {
      isNew: false,
      query: {
        categories: null,
        date: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        orderBy: 'offer.id+desc',
      },
    }
    const toto = 'jours'
    const tata = '1-5'
    const callback = jest.fn()

    // const props = {
    //   pagination: {
    //
    //   }
    // }
    it('should XXXXXXXXXXXX ', () => {
      expect(handleQueryAdd(toto, tata, currentState, callback)).toEqual(
        'jours'
      )
    })
  })
})
