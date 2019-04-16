import React from 'react'
import { shallow } from 'enzyme'

import Deck from '../Deck'

const dispatchMock = jest.fn()
const handleDataRequestMock = jest.fn()

describe('src | components | pages | discovery | deck | Deck', () => {
  const initialProps = {
    areDetailsVisible: false,
    backButton: true,
    currentRecommendation: {},
    dispatch: dispatchMock,
    draggable: true,
    handleDataRequest: handleDataRequestMock,
    height: 947,
    history: {
      location: {
        search: '',
      },
    },
    isFlipDisabled: false,
    match: { params: {} },
    nextLimit: 50,
    previousLimit: 40,
    recommendations: [{}],
    unFlippable: false,
    width: 500,
  }

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Deck {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
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
        expect(wrapper.state()).toEqual(expected)
        expect(wrapper.instance().currentReadRecommendationId).toEqual(null)
      })
    })

    describe('componentDidMount', () => {
      describe('Whenever', () => {
        it('should call handleUrlFlip', async () => {
          // given
          const props = {
            areDetailsVisible: false,
            backButton: true,
            dispatch: dispatchMock,
            draggable: true,
            handleDataRequest: handleDataRequestMock,
            height: 947,
            history: {
              location: {
                search: '',
              },
            },
            isFlipDisabled: false,
            match: {
              params: {
                mediationId: 'HM',
                offerId: 'KQ',
              },
            },
            nextLimit: 50,
            previousLimit: 40,
            recommendations: [],
            unFlippable: false,
            width: 500,
          }

          // when
          const wrapper = shallow(<Deck {...props} />)
          const wrapperInstance = wrapper.instance()
          const spy = jest
            .spyOn(wrapperInstance, 'handleUrlFlip')
            .mockImplementation(() => {})
          wrapper.setProps(props)
          // setProps() make the componentDidMount after instanciating the spy

          // then
          expect(spy).toHaveBeenCalled()
        })
      })

      describe('When there is recommendations', () => {
        it('should not refresh the key of draggable component', () => {
          // given
          const props = {
            areDetailsVisible: false,
            backButton: true,
            currentRecommendation: {
              bookingsIds: [],
            },
            dispatch: dispatchMock,
            draggable: true,
            handleDataRequest: handleDataRequestMock,
            height: 947,
            history: {
              location: {
                search: '',
              },
            },
            isFlipDisabled: false,
            match: {
              params: {
                mediationId: 'HM',
                offerId: 'KQ',
              },
            },
            nextLimit: 50,
            previousLimit: 40,
            recommendations: [{}],
            unFlippable: false,
            width: 500,
          }

          // when
          const wrapper = shallow(<Deck {...props} />)

          // then
          expect(wrapper.state()).toEqual({ refreshKey: 0 })
        })
      })

      describe('When there is no recommendations or currentRecommendation available', () => {
        it('should call handleRefreshedDraggableKey', () => {
          // given
          const props = {
            areDetailsVisible: false,
            backButton: true,
            dispatch: dispatchMock,
            draggable: true,
            handleDataRequest: handleDataRequestMock,
            height: 947,
            history: {
              location: {
                search: '',
              },
            },
            isFlipDisabled: false,
            match: {
              params: {
                mediationId: 'HM',
                offerId: 'KQ',
              },
            },
            nextLimit: 50,
            previousLimit: 40,
            recommendations: [],
            unFlippable: false,
            width: 500,
          }

          // when
          const wrapper = shallow(<Deck {...props} />)
          wrapper.setProps(props)

          // then
          expect(wrapper.state()).toEqual({ refreshKey: 1 })
        })
      })
    })

    describe('componentWillUnmount', () => {
      it('should dispatch unFlip', () => {
        // when
        const wrapper = shallow(<Deck {...initialProps} />)
        wrapper.unmount()

        // then
        expect(dispatchMock.mock.calls.length).toBe(1)
        expect(dispatchMock).toHaveBeenCalledWith({
          type: 'CLOSE_DETAILS_VIEW',
        })
      })

      it('should clearTimeout', () => {
        jest.useFakeTimers()
        // when
        const wrapper = shallow(<Deck {...initialProps} />)
        wrapper.unmount()

        // then
        expect(clearTimeout).toHaveBeenCalled()
      })
    })
  })
})
