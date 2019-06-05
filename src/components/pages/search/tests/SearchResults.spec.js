import { shallow } from 'enzyme'
import React from 'react'

import { SearchResults } from '../SearchResults'
import { SearchResultItemContainer } from '../SearchResultItemContainer'

describe('src | components | pages | search | SearchResults', () => {
  let props

  beforeEach(() => {
    props = {
      cameFromOfferTypesPage: true,
      hasMore: false,
      items: [],
      keywords: 'fakeKeywords',
      query: {
        add: jest.fn(),
        change: jest.fn(),
        clear: jest.fn(),
        parse: () => ({ page: '1' }),
        remove: jest.fn(),
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    props.cameFromOfferTypesPage = false

    // when
    const wrapper = shallow(<SearchResults {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleSetHasReceivedFirstSuccessData()', () => {
    it('should return hasReceivedFirstSuccessData = true if there are data', () => {
      // given
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ hasReceivedFirstSuccessData: false })

      // when
      wrapper.instance().handleSetHasReceivedFirstSuccessData()

      // then
      expect(wrapper.state(['hasReceivedFirstSuccessData'])).toBe(true)
    })

    it('should return undefined if there are no data', () => {
      // given
      const wrapper = shallow(<SearchResults {...props} />)

      // when
      wrapper.setState({ hasReceivedFirstSuccessData: true })
      const handleSetHasReceivedFirstSuccessData = wrapper
        .instance()
        .handleSetHasReceivedFirstSuccessData()

      // then
      expect(handleSetHasReceivedFirstSuccessData).toBeUndefined()
    })
  })

  describe('handleShouldCancelLoading()', () => {
    it('should return isLoading = false if its loading', () => {
      // given
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ isLoading: true })

      // when
      wrapper.instance().handleShouldCancelLoading()

      // then
      expect(wrapper.state(['isLoading'])).toBe(false)
    })

    it('should return undefined if its not loading', () => {
      // given
      const wrapper = shallow(<SearchResults {...props} />)

      // when
      const handleShouldCancelLoading = wrapper
        .instance()
        .handleShouldCancelLoading()

      // then
      expect(handleShouldCancelLoading).toBeUndefined()
    })
  })

  describe('loadMore()', () => {
    const page = 10

    it('should return undefined if its loading', () => {
      // given
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ isLoading: true })

      // when
      const loadMore = wrapper.instance().loadMore(page)

      // then
      expect(loadMore).toBeUndefined()
    })

    it('should called query change if its not loading', () => {
      // given
      const wrapper = shallow(<SearchResults {...props} />)

      // when
      wrapper.instance().loadMore(page)

      // then
      expect(wrapper.state(['isLoading'])).toBe(true)
      expect(props.query.change).toBeCalledWith(
        { page },
        { historyMethod: 'replace' }
      )
    })
  })

  describe('render()', () => {
    const items = [
      {
        offerId: 'Q4',
      },
    ]

    describe('with navigation by offer types mode', () => {
      describe('when there is items', () => {
        it('should not render title', () => {
          // given
          props.items = items
          const wrapper = shallow(<SearchResults {...props} />)

          // when
          const resultsTitle = wrapper.is('h2')
          const SearchResultItemWrapper = wrapper.find(
            SearchResultItemContainer
          )
          const item = {
            recommendation: items[0],
          }

          // then
          expect(resultsTitle).toBe(false)
          expect(SearchResultItemWrapper.props()).toEqual(item)
        })
      })

      describe('when there is no result', () => {
        it('should render properly the result title with no item', () => {
          // given
          const wrapper = shallow(<SearchResults {...props} />)

          // when
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const SearchResultItemWrapper = wrapper.find(
            SearchResultItemContainer
          )

          // then
          expect(resultsTitle.children).toEqual(
            "Il n'y a pas d'offres dans cette catégorie pour le moment."
          )
          expect(SearchResultItemWrapper.length).toEqual(0)
        })
      })
    })

    describe('without navigation by offer types mode', () => {
      describe('when there is a result with only key words', () => {
        it('should render properly the result title and item', () => {
          // given
          props.cameFromOfferTypesPage = false
          props.items = items
          const wrapper = shallow(<SearchResults {...props} />)

          // when
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const SearchResultItemWrapper = wrapper.find(
            SearchResultItemContainer
          )
          const item = {
            recommendation: items[0],
          }

          // then
          expect(resultsTitle.children).toEqual('"fakeKeywords" : 1 résultat')
          expect(SearchResultItemWrapper.props()).toEqual(item)
        })
      })

      describe('when there is no result', () => {
        it('should render properly the result title with no item', () => {
          // given
          props.cameFromOfferTypesPage = false
          const wrapper = shallow(<SearchResults {...props} />)

          // when
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const SearchResultItemWrapper = wrapper.find(
            SearchResultItemContainer
          )

          // then
          expect(resultsTitle.children).toEqual('"fakeKeywords" : 0 résultat')
          expect(SearchResultItemWrapper.length).toEqual(0)
        })
      })
    })
  })
})
