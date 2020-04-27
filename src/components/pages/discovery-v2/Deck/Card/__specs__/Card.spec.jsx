import React from 'react'
import { shallow } from 'enzyme'

import Card from '../Card'

describe('src | components | pages | discovery | Deck | Card', () => {
  describe('when mount', () => {
    it('should call handleSeenOffer once when feature is active and card is on current recommendation', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        isSeenOfferFeatureActive: true,
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
    it('should not call handleSeenOffer when card is not on current recommendation', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        isSeenOfferFeatureActive: true,
        match: { params: {} },
        position: 'previous',
        width: 500,
        handleSeenOffer: jest.fn(),
        seenOffer: {},
        recommendation: {},
      }

      // when
      shallow(<Card {...props} />)

      // then
      expect(props.handleSeenOffer).not.toHaveBeenCalled()
    })
    it('should not call handleSeenOffer when current card does not have recommendation', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        isSeenOfferFeatureActive: true,
        match: { params: {} },
        position: 'current',
        width: 500,
        handleSeenOffer: jest.fn(),
        seenOffer: {},
      }

      // when
      shallow(<Card {...props} />)

      // then
      expect(props.handleSeenOffer).not.toHaveBeenCalled()
    })
    it('should not call handleSeenOffer when seen offer feature is not active', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        isSeenOfferFeatureActive: false,
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
      expect(props.handleSeenOffer).not.toHaveBeenCalled()
    })
  })
  describe('when update', () => {
    it('should call handleSeenOffer on new recommendation', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        handleSeenOffer: jest.fn(),
        isSeenOfferFeatureActive: true,
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
        isSeenOfferFeatureActive: true,
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
        isSeenOfferFeatureActive: true,
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

    it('should not call handleSeenOffer when seen offer feature is not active', () => {
      // given
      const props = {
        handleClickRecommendation: jest.fn(),
        handleReadRecommendation: jest.fn(),
        handleSeenOffer: jest.fn(),
        isSeenOfferFeatureActive: false,
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
      expect(props.handleSeenOffer).not.toHaveBeenCalled()
    })
  })
})
