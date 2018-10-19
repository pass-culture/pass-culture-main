import { searchResultsTitle } from '../utils'

describe('searchResultsTitle', () => {
  // given
  let items
  let keywords
  let queryParams
  let result
  let expected
  describe('with keyword search field or filter', () => {
    const withPagination = false // FOR CALLS

    describe('when there is a keywords but no filters', () => {
      describe('with a search results', () => {
        it('should return a title for search results', () => {
          // given
          items = [{}, {}, {}, {}]
          keywords = 'keyword'

          queryParams = {
            categories: null,
            date: null,
            days: null,
            distance: null,
            jours: null,
            latitude: null,
            longitude: null,
            [`mots-cles`]: 'keyword',
            page: '2',
            types: null,
          }

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            withPagination
          )
          expected = '"keyword" : 4 résultats'

          // then
          expect(result).toEqual(expected)
        })
      })

      describe('without no results', () => {
        it('should return a title for search results', () => {
          // given
          items = []
          keywords = 'keyword'
          queryParams = {
            categories: null,
            date: null,
            days: null,
            distance: null,
            jours: null,
            latitude: null,
            longitude: null,
            [`mots-cles`]: 'keyword',
            page: '2',
            types: null,
          }

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            withPagination
          )
          expected = '"keyword" : 0 résultat'

          // then
          expect(result).toEqual(expected)
        })
      })
    })

    describe('when there is a keyword plus one or more filters', () => {
      describe('with items in results', () => {
        it('should return a title for search results', () => {
          // given
          items = [{}, {}, {}, {}]
          keywords = 'keyword'

          queryParams = {
            categories: 'Applaudir',
            date: null,
            days: null,
            distance: null,
            jours: null,
            latitude: null,
            longitude: null,
            [`mots-cles`]: 'keyword',
            page: '2',
            types: null,
          }

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            withPagination
          )
          expected = '"keyword" : 4 résultats'

          // then
          expect(result).toEqual(expected)
        })
      })

      describe('without items', () => {
        it('should return a title for search results', () => {
          // given
          items = []
          keywords = 'keyword'
          queryParams = {
            categories: 'Jouer',
            date: null,
            days: null,
            distance: null,
            jours: null,
            latitude: null,
            longitude: null,
            [`mots-cles`]: 'keyword',
            page: '2',
            types: null,
          }

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            withPagination
          )
          expected = '"keyword" : 0 résultat'

          // then
          expect(result).toEqual(expected)
        })
      })
    })
  })

  describe('with navigation mode', () => {
    keywords = 'fake word'
    queryParams = {
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
    const withPagination = true

    describe('with a search results', () => {
      it('should return an empty string', () => {
        // given
        items = [{}]

        // when
        result = searchResultsTitle(
          keywords,
          items,
          queryParams,
          withPagination
        )
        expected = ''

        // then
        expect(result).toEqual(expected)
      })
    })
    describe('without no results', () => {
      it('should return a message that inform that there is no offers for the moment', () => {
        // given
        items = []

        // when
        result = searchResultsTitle(
          keywords,
          items,
          queryParams,
          withPagination
        )
        expected = "Il n'y a pas d'offres dans cette catégorie pour le moment."

        // then
        expect(result).toEqual(expected)
      })
    })
  })
})
