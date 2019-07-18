import { shallow } from 'enzyme'
import React from 'react'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyFavorites from '../MyFavorites'
import NavigationFooter from '../../../layout/NavigationFooter'
import NoFavorites from '../NoFavorites'
import PageHeader from '../../../layout/Header/PageHeader'

describe('src | components | pages | my-favorites | MyFavorites', () => {
  let props

  beforeEach(() => {
    props = {
      getMyFavorites: jest.fn(),
      myFavorites: [
        {
          id: 1,
        },
      ],
    }
  })

  describe('handleFail()', () => {
    it('should handle fail', () => {
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
    it('should handle success', () => {
      // given
      const wrapper = shallow(<MyFavorites {...props} />)

      // when
      wrapper.instance().handleSuccess({}, { payload: { data: [] } })

      // then
      expect(wrapper.state('isEmpty')).toBe(true)
      expect(wrapper.state('isLoading')).toBe(false)
    })
  })

  describe('render()', () => {
    it('should render my favorites', () => {
      // when
      const wrapper = shallow(<MyFavorites {...props} />)
      wrapper.setState({ isLoading: false })

      // then
      const pageHeader = wrapper.find(PageHeader)
      const ul = wrapper.find('ul')
      const navigationFooter = wrapper.find(NavigationFooter)
      expect(pageHeader).toHaveLength(1)
      // expect(ul).toHaveLength(2)
      expect(navigationFooter).toHaveLength(1)
    })

    it('should render the Loader when there is something wrong with API', () => {
      // when
      const wrapper = shallow(<MyFavorites {...props} />)

      // then
      const loaderContainer = wrapper.find(LoaderContainer)
      expect(loaderContainer).toHaveLength(1)
    })

    it('should not render my favorites when there are no favorites', () => {
      // given
      props.myFavorites = []

      // when
      const wrapper = shallow(<MyFavorites {...props} />)
      wrapper.setState({
        isEmpty: true,
        isLoading: false,
      })

      // then
      const noFavorites = wrapper.find(NoFavorites)
      expect(noFavorites).toHaveLength(1)
    })
  })
})
