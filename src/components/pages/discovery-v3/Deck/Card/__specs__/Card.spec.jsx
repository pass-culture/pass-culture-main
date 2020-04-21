import React from 'react'
import { shallow } from 'enzyme'

import Card from '../Card'

describe('src | components | pages | discovery | Deck | Card', () => {
  describe('when mount', () => {
    it('should call handleSeenOffer once', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        match: { params: {} },
        position: 'current',
        width: 500,
        handleSeenOffer: jest.fn(),
        seenOffer: {},
        recommendation: {},
      }

      // when
      shallow(<Card {...props} />)

      // then
      expect(props.handleSeenOffer).toHaveBeenCalledTimes(1)
      expect(props.handleSeenOffer).toHaveBeenCalledWith(props.seenOffer)
    })
  })
  describe('when update', () => {
    it('should call handleSeenOffer on new recommendation', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        handleSeenOffer: jest.fn(),
        match: { params: {} },
        position: 'position',
        width: 500,
        seenOffer: {},
        recommendation: {},
      }
      const wrapper = shallow(<Card {...props} />)
      props.handleSeenOffer.mockClear()

      // when
      wrapper.setProps({
        recommendation: { id: 'TE23' },
        position: 'previous',
      })

      // then
      expect(props.handleSeenOffer).toHaveBeenCalledTimes(1)
      expect(props.handleSeenOffer).toHaveBeenCalledWith(props.seenOffer)
    })

    it('should not call handleSeenOffer when recommendation is not updated', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        handleSeenOffer: jest.fn(),
        match: { params: {} },
        position: 'current',
        width: 500,
        seenOffer: {},
        recommendation: { id: 'GE5' },
      }
      const wrapper = shallow(<Card {...props} />)
      props.handleSeenOffer.mockClear()

      // when
      wrapper.setProps({
        position: 'previous',
      })

      // then
      expect(props.handleSeenOffer).toHaveBeenCalledTimes(0)
    })

    it('should not call handleSeenOffer when position is not on previous card', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        handleSeenOffer: jest.fn(),
        match: { params: {} },
        position: 'current',
        width: 500,
        seenOffer: {},
        recommendation: { id: 'UZ7' },
      }
      const wrapper = shallow(<Card {...props} />)
      props.handleSeenOffer.mockClear()

      // when
      wrapper.setProps({
        recommendation: { id: 'TE23' },
      })

      // then
      expect(props.handleSeenOffer).toHaveBeenCalledTimes(0)
    })
  })
})
