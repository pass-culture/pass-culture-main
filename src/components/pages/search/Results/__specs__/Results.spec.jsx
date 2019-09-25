import { shallow } from 'enzyme'
import React from 'react'

import Results from '../Results'
import TeaserContainer from '../../../../layout/Teaser/TeaserContainer'

describe('src | components | pages | search | Results', () => {
  let props

  beforeEach(() => {
    props = {
      cameFromOfferTypesPage: true,
      hasMore: false,
      history: {
        replace: jest.fn(),
      },
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
    const wrapper = shallow(<Results {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleSetHasReceivedFirstSuccessData()', () => {
    it('should return hasReceivedFirstSuccessData = true if there are data', () => {
      // given
      const wrapper = shallow(<Results {...props} />)
      wrapper.setState({ hasReceivedFirstSuccessData: false })

      // when
      wrapper.instance().handleSetHasReceivedFirstSuccessData()

      // then
      expect(wrapper.state(['hasReceivedFirstSuccessData'])).toBe(true)
    })

    it('should return undefined if there are no data', () => {
      // given
      const wrapper = shallow(<Results {...props} />)

      // when
      wrapper.setState({ hasReceivedFirstSuccessData: true })
      const handleSetHasReceivedFirstSuccessData = wrapper
        .instance()
        .handleSetHasReceivedFirstSuccessData()

      // then
      expect(handleSetHasReceivedFirstSuccessData).toBeUndefined()
    })
  })

  describe('handleSetHasMore', () => {
    it('should set state to false is there less than 10 items in new batch', () => {
      // given
      const wrapper = shallow(<Results {...props} />)
      const itemLength = 4

      // when
      wrapper.instance().handleSetHasMore(itemLength)

      // then
      expect(wrapper.state(['hasMore'])).toBe(false)
    })

    it('should set state to true is there are 10 items in new batch', () => {
      // given
      const wrapper = shallow(<Results {...props} />)
      const itemLength = 10

      // when
      wrapper.instance().handleSetHasMore(itemLength)

      // then
      expect(wrapper.state(['hasMore'])).toBe(true)
    })
  })

  describe('handleShouldCancelLoading()', () => {
    it('should return isLoading = false if its loading', () => {
      // given
      const wrapper = shallow(<Results {...props} />)
      wrapper.setState({ isLoading: true })

      // when
      wrapper.instance().handleShouldCancelLoading()

      // then
      expect(wrapper.state(['isLoading'])).toBe(false)
    })

    it('should return undefined if its not loading', () => {
      // given
      const wrapper = shallow(<Results {...props} />)

      // when
      const handleShouldCancelLoading = wrapper.instance().handleShouldCancelLoading()

      // then
      expect(handleShouldCancelLoading).toBeUndefined()
    })
  })

  describe('loadMore()', () => {
    const page = 10

    it('should return undefined if its loading', () => {
      // given
      const wrapper = shallow(<Results {...props} />)
      wrapper.setState({ isLoading: true })

      // when
      const loadMore = wrapper.instance().loadMore(page)

      // then
      expect(loadMore).toBeUndefined()
    })

    it('should called query change if its not loading', () => {
      // given
      const wrapper = shallow(<Results {...props} />)

      // when
      wrapper.instance().loadMore(page)

      // then
      expect(wrapper.state(['isLoading'])).toBe(true)
      expect(props.query.change).toHaveBeenCalledWith({ page }, { historyMethod: 'replace' })
    })
  })

  describe('render()', () => {
    const items = [
      {
        offerId: 'Q4',
        id: 'id',
      },
    ]

    describe('with navigation by offer types mode', () => {
      describe('when there is items', () => {
        it('should not render title', () => {
          // given
          props.items = items
          const wrapper = shallow(<Results {...props} />)

          // when
          const resultsTitle = wrapper.is('h2')
          const searchTeaserContainer = wrapper.find(TeaserContainer)
          const searchResult = {
            item: items[0],
          }

          // then
          expect(resultsTitle).toBe(false)
          expect(searchTeaserContainer.props()).toStrictEqual(searchResult)
        })
      })

      describe('when there is no result', () => {
        it('should render properly the result title with no item', () => {
          // given
          const wrapper = shallow(<Results {...props} />)

          // when
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const searchTeaserContainer = wrapper.find(TeaserContainer)

          // then
          expect(resultsTitle.children).toBe(
            'Il n’y a pas d’offres dans cette catégorie pour le moment.'
          )
          expect(searchTeaserContainer).toHaveLength(0)
        })
      })
    })

    describe('without navigation by offer types mode', () => {
      describe('when there is a result with only key words', () => {
        it('should render properly the result title and item', () => {
          // given
          props.cameFromOfferTypesPage = false
          props.items = items
          const wrapper = shallow(<Results {...props} />)

          // when
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const searchTeaserContainer = wrapper.find(TeaserContainer)
          const searchResult = {
            item: items[0],
          }

          // then
          expect(resultsTitle.children).toBe('"fakeKeywords" : 1 résultat')
          expect(searchTeaserContainer.props()).toStrictEqual(searchResult)
        })
      })

      describe('when there is no result', () => {
        it('should render properly the result title with no item', () => {
          // given
          props.cameFromOfferTypesPage = false
          const wrapper = shallow(<Results {...props} />)

          // when
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const searchTeaserContainer = wrapper.find(TeaserContainer)

          // then
          expect(resultsTitle.children).toBe('"fakeKeywords" : 0 résultat')
          expect(searchTeaserContainer).toHaveLength(0)
        })
      })
    })
  })
})
