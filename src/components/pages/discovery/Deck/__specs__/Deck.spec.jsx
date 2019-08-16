import React from 'react'
import { shallow } from 'enzyme'

import Deck from '../Deck'

const dispatchMock = jest.fn()
const handleRequestPutRecommendationsMock = jest.fn()

describe('src | components | pages | discovery | Deck | Deck', () => {
  const initialProps = {
    backButton: true,
    currentRecommendation: {},
    dispatch: dispatchMock,
    draggable: true,
    handleRequestPutRecommendations: handleRequestPutRecommendationsMock,
    height: 947,
    history: {
      push: jest.fn()
    },
    isFlipDisabled: false,
    location: {
      pathname: '',
      search: '',
    },
    match: {
      params: {}
    },
    nextLimit: 50,
    previousLimit: 40,
    recommendations: [{}],
    width: 500,
  }

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Deck {...initialProps} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('react functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // when
        const wrapper = shallow(<Deck {...initialProps} />)
        const expected = {
          refreshKey: 0,
        }

        // then
        expect(wrapper.state()).toStrictEqual(expected)
        expect(wrapper.instance().currentReadRecommendationId).toStrictEqual(null)
      })
    })

    describe('componentDidMount', () => {
      describe('when there is recommendations', () => {
        it('should not refresh the key of draggable component', () => {
          // given
          const props = {
            backButton: true,
            currentRecommendation: {
              bookingsIds: [],
            },
            dispatch: dispatchMock,
            draggable: true,
            handleRequestPutRecommendations: handleRequestPutRecommendationsMock,
            height: 947,
            history: {
              push: jest.fn()
            },
            isFlipDisabled: false,
            location: {
              pathname: '',
              search: '',
            },
            match: {
              params: {
                mediationId: 'HM',
                offerId: 'KQ',
              },
            },
            nextLimit: 50,
            previousLimit: 40,
            recommendations: [{}],
            width: 500,
          }

          // when
          const wrapper = shallow(<Deck {...props} />)

          // then
          expect(wrapper.state()).toStrictEqual({ refreshKey: 0 })
        })
      })

      describe('when there is no recommendations or currentRecommendation available', () => {
        it('should call handleRefreshedDraggableKey', () => {
          // given
          const props = {
            backButton: true,
            dispatch: dispatchMock,
            draggable: true,
            handleRequestPutRecommendations: handleRequestPutRecommendationsMock,
            height: 947,
            history: {
              push: jest.fn()
            },
            isFlipDisabled: false,
            location: {
              pathname: '',
              search: '',
            },
            match: {
              params: {
                mediationId: 'HM',
                offerId: 'KQ',
              },
            },
            nextLimit: 50,
            previousLimit: 40,
            recommendations: [],
            width: 500,
          }

          // when
          const wrapper = shallow(<Deck {...props} />)
          wrapper.setProps(props)

          // then
          expect(wrapper.state()).toStrictEqual({ refreshKey: 1 })
        })
      })
    })

    describe('componentWillUnmount', () => {
      it('should clearTimeout', () => {
        jest.useFakeTimers()
        // when
        const wrapper = shallow(<Deck {...initialProps} />)
        wrapper.unmount()

        // then
        expect(clearTimeout).toHaveBeenCalledWith(2000)
      })
    })
  })
})
