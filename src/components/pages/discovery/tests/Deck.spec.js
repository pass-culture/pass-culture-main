import React from 'react'
import { shallow } from 'enzyme'

import { RawDeck } from '../Deck'

const dispatchMock = jest.fn()

describe('src | components | pages | discovery | Index | DiscoveryPage', () => {
  // given
  const initialProps = {
    backButton: true,
    dispatch: dispatchMock,
    draggable: true,
    height: 947,
    history: {
      location: {
        search: '',
      },
    },
    isFlipDisabled: false,
    isFlipped: false,
    match: {},
    nextLimit: 50,
    previousLimit: 40,
    recommendations: [],
    unFlippable: false,
    width: 500,
  }

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RawDeck {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  // describe('render', () => {
  //
  // })
  describe('react functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        const wrapper = shallow(<RawDeck {...initialProps} />)
        const expected = {
          refreshKey: 0,
        }

        // then
        expect(wrapper.state()).toEqual(expected)
        expect(wrapper.instance().currentReadRecommendationId).toEqual(null)
      })
    })
    describe('componentDidMount', () => {
      describe('Each time the component dit mount', () => {
        it('should call handleUrlFlip with history', async () => {
          // given
          const props = {
            backButton: true,
            dispatch: dispatchMock,
            draggable: true,
            height: 947,
            history: {
              location: {
                search: '',
              },
            },
            isFlipDisabled: false,
            isFlipped: false,
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
          const history = props.history

          // when
          const wrapper = shallow(<RawDeck {...props} />)
          const wrapperInstance = wrapper.instance()
          const spy = jest
            .spyOn(wrapperInstance, 'handleUrlFlip')
            .mockImplementation(() => {})
          wrapper.setProps(props)
          // setProps() make the componentDidMount after instanciating the spy
          expect(spy).toHaveBeenCalledWith(history, history)
        })
      })
      describe('When ------> add condition', () => {
        it('should call handleRefreshedData', () => {
          // given
          const props = {
            backButton: true,
            dispatch: dispatchMock,
            draggable: true,
            height: 947,
            history: {
              location: {
                search: '',
              },
            },
            isFlipDisabled: false,
            isFlipped: false,
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
          const wrapper = shallow(<RawDeck {...props} />)
          const wrapperInstance = wrapper.instance()
          const spy = jest
            .spyOn(wrapperInstance, 'handleRefreshedData')
            .mockImplementation(() => {})
          wrapper.setProps(props)
          // setProps() make the componentDidMount after instanciating the spy
          expect(spy).toHaveBeenCalled()
        })
      })
    })
    describe('componentDidUpdate', () => {
      describe('When query search contains to=verso', () => {
        it('should dispatch handleUrlFlip', () => {
          // given
          const props = {
            backButton: true,
            dispatch: dispatchMock,
            draggable: true,
            height: 947,
            history: {
              location: {
                search: '',
              },
            },
            isFlipDisabled: false,
            isFlipped: false,
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

          const newProps = {
            history: {
              location: {
                key: 'odnw65',
                pathname: '/decouverte/J9/GY',
                search: '?to=verso',
              },
            },
            isFlipped: true,
          }
          const wrapper = shallow(<RawDeck {...props} />)
          const wrapperInstance = wrapper.instance()
          const spy = jest
            .spyOn(wrapperInstance, 'handleUrlFlip')
            .mockImplementation(() => {})

          wrapper.setProps(newProps)
          const history = newProps.history
          const previousHistory = props.history

          expect(spy).toHaveBeenCalledWith(history, previousHistory)
          // expect(dispatchMock.mock.calls.length).toBe(1)

          // expect(dispatchMock.mock.calls[0][0]).toEqual(
          // expectedRequest
          // )

          // expect(dispatchMock).toHaveBeenCalledWith(expectedRequest)
        })
      })
    })
    describe('componentWillUnmount', () => {})

    // describe('handleDataRequest', () => {
    //   describe('One case', () => {
    //     it('should first dispatch requestData when  Main component is rendered', () => {
    //       // given
    //       const props = {
    //         backButton: true,
    //         dispatch: dispatchMock,
    //         history: {},
    //         match: {},
    //       }
    //
    //       // when
    //       const wrapper = shallow(<RawDeck {...props} />)
    //       wrapper.instance().handleDataRequest()
    //       const expectedRequest = {
    //         config: {},
    //         method: 'PUT',
    //         path: 'recommendations?',
    //         type: 'REQUEST_DATA_PUT_RECOMMENDATIONS?',
    //       }
    //
    //       // then
    //       expect(dispatchMock.mock.calls.length).toBe(1)
    //       expect(dispatchMock.mock.calls[0][0].method).toEqual(
    //         expectedRequest.method
    //       )
    //     })
    //   })
    // })
  })
})
