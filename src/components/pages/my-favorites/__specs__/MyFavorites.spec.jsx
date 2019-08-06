import { shallow } from 'enzyme'
import React from 'react'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyFavoriteContainer from '../MyFavorite/MyFavoriteContainer'
import MyFavorites from '../MyFavorites'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import NoItems from '../../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

describe('src | components | pages | my-favorites | MyFavorites', () => {
  let props

  beforeEach(() => {
    props = {
      myFavorites: [
        {
          id: 1,
          offerId: 'ME',
          offer: {
            id: 'ME',
            name: 'name',
          },
          mediationId: 'FA',
          mediation: {
            id: 'FA',
            thumbUrl: 'thumbUrl',
          },
        },
        {
          id: 2,
          offerId: 'ME',
          offer: {
            id: 'ME',
            name: 'name',
          },
          mediationId: 'FA',
          mediation: {
            id: 'FA',
            thumbUrl: 'thumbUrl',
          },
        },
      ],
      requestGetMyFavorites: jest.fn(),
      resetPageData: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<MyFavorites {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleFail()', () => {
    it('should set hasError and isLoading to true in component state', () => {
      // given
      const wrapper = shallow(<MyFavorites {...props} />)

      // when
      wrapper.instance().handleFail()

      // then
      expect(wrapper.state('hasError')).toBe(true)
      expect(wrapper.state('isLoading')).toBe(true)
    })
  })

  describe('handleSuccess()', () => {
    it('should set isLoading to false in component state', () => {
      // given
      const wrapper = shallow(<MyFavorites {...props} />)

      // when
      wrapper.instance().handleSuccess({}, { payload: { data: [] } })

      // then
      expect(wrapper.state('isLoading')).toBe(false)
    })
  })

  describe('render()', () => {
    it('should render my favorites', () => {
      // when
      const wrapper = shallow(<MyFavorites {...props} />)
      wrapper.setState({ isLoading: false })

      // then
      const header = wrapper.find(HeaderContainer)
      const ul = wrapper.find('ul')
      const footer = wrapper.find(RelativeFooterContainer)
      expect(header).toHaveLength(1)
      expect(ul).toHaveLength(1)
      expect(footer).toHaveLength(1)
    })

    describe('when there is something wrong with API', () => {
      it('should render the Loader', () => {
        // when
        const wrapper = shallow(<MyFavorites {...props} />)

        // then
        const loaderContainer = wrapper.find(LoaderContainer)
        expect(loaderContainer).toHaveLength(1)
      })
    })

    describe('when there are no favorites', () => {
      it('should not render my favorites', () => {
        // given
        props.myFavorites = []

        // when
        const wrapper = shallow(<MyFavorites {...props} />)
        wrapper.setState({
          isLoading: false,
        })

        // then
        const noItems = wrapper.find(NoItems)
        expect(noItems).toHaveLength(1)
        const myFavoriteContainer = wrapper.find(MyFavoriteContainer)
        expect(myFavoriteContainer).toHaveLength(0)
      })
    })
  })
})
