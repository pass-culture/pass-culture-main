import React from 'react'
import { shallow } from 'enzyme'

import Deck from '../Deck'
import CloseLink from '../../../../layout/Header/CloseLink/CloseLink'

describe('src | components | pages | discovery | Deck | Deck', () => {
  let props

  beforeEach(() => {
    props = {
      currentRecommendation: {
        bookingsIds: [],
        offerId: 'ABCD',
      },
      handleRequestPutRecommendations: jest.fn(),
      height: 947,
      history: {
        push: jest.fn(),
        replace: jest.fn(),
      },
      isFlipDisabled: false,
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {},
      },
      nextLimit: 50,
      nextRecommendation: null,
      noDataTimeout: 2000,
      readTimeout: 2000,
      recommendations: [{}],
      verticalSlideRatio: 0.1,
      width: 500,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Deck {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a Deck component with a default state', () => {
      // when
      const wrapper = shallow(<Deck {...props} />)

      // then
      expect(wrapper.state()).toStrictEqual({
        refreshKey: 0,
      })
    })

    it('should render a CloseLink component with the right props when card detail is visible', () => {
      // given
      props.location = {
        pathname: '/fake-url',
        search: '',
      }
      props.match = {
        params: {
          details: 'details',
        },
      }

      // when
      const wrapper = shallow(<Deck {...props} />)

      // then
      const closeLink = wrapper.find(CloseLink)
      expect(closeLink).toHaveLength(1)
      expect(closeLink.prop('closeTitle')).toBe('Fermer')
      expect(closeLink.prop('closeTo')).toBe('/fake-url/transition')
    })

    it('should replace url when Deck component is updated and current url contains "transition" as query param', () => {
      // given
      props.location = {
        pathname: '/fake-url',
        search: '',
      }
      props.match = {
        params: {
          details: 'transition',
        },
      }
      const wrapper = shallow(<Deck {...props} />)
      props.areDetailsVisible = false

      // when
      wrapper.setProps({ ...props })

      // then
      expect(props.history.replace).toHaveBeenCalledWith('/fake-url')
    })

    it('should not replace url when Deck component is updated and current url does not contains "transition" as query param', () => {
      // given
      props.location = {
        pathname: '/fake-url',
        search: '',
      }
      props.match = {
        params: {
          details: '',
        },
      }
      const wrapper = shallow(<Deck {...props} />)
      props.areDetailsVisible = false

      // when
      wrapper.setProps({ ...props })

      // then
      expect(props.history.replace).not.toHaveBeenCalledWith()
    })
  })

  describe('componentWillUnmount', () => {
    it('should clearTimeout', () => {
      // given
      jest.useFakeTimers()
      const wrapper = shallow(<Deck {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(clearTimeout).toHaveBeenCalledWith(2000)
    })
  })
})
