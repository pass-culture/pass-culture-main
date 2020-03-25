import React from 'react'
import { shallow } from 'enzyme'

import Discovery from '../Discovery'

describe('src | components | pages | discovery | Discovery', () => {
  let props

  beforeEach(() => {
    props = {
      coordinates: {
        longitude: 48.256756,
        latitude: 2.8796567,
        watchId: 1,
      },
      currentRecommendation: {},
      deleteTutorials: jest.fn(),
      loadRecommendations: jest.fn(),
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {},
      },
      readRecommendations: [],
      recommendations: [],
      redirectToFirstRecommendationIfNeeded: jest.fn(),
      resetReadRecommendations: jest.fn(),
      resetRecommendations: jest.fn(),
      resetRecommendationsAndBookings: jest.fn(),
      saveLastRecommendationsRequestTimestamp: jest.fn(),
      seedLastRequestTimestamp: 1574236357670,
      shouldReloadRecommendations: false,
      tutorials: [],
      updateLastRequestTimestamp: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Discovery {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('constructor', () => {
    it('should initialize state with default values', () => {
      // given
      const wrapper = shallow(<Discovery {...props} />)

      // then
      expect(wrapper.state()).toStrictEqual({
        atWorldsEnd: false,
        hasError: false,
        isEmpty: null,
        isLoading: false,
      })
    })
  })

  describe('when mount', () => {
    it('should load recommendations when it is required to fetch recommendations', () => {
      // given
      props.shouldReloadRecommendations = true

      // when
      shallow(<Discovery {...props} />)

      // then
      expect(props.loadRecommendations).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function),
        props.currentRecommendation,
        props.recommendations,
        props.readRecommendations,
        props.shouldReloadRecommendations,
        props.coordinates
      )
      expect(props.saveLastRecommendationsRequestTimestamp).toHaveBeenCalledWith()
    })

    it('should redirect to first recommendation when it is not required to fetch recommendations', () => {
      // given
      props.shouldReloadRecommendations = false

      // when
      shallow(<Discovery {...props} />)

      // then
      expect(props.loadRecommendations).not.toHaveBeenCalledWith()
      expect(props.saveLastRecommendationsRequestTimestamp).not.toHaveBeenCalledWith()
      expect(props.redirectToFirstRecommendationIfNeeded).toHaveBeenCalledWith(
        props.recommendations
      )
    })
  })

  describe('when unmount', () => {
    it('should delete tutorials for current user', () => {
      // given
      props.tutorials = [
        {
          id: 'hello',
          productOrTutoIdentifier: 'tuto_0',
        },
      ]
      const wrapper = shallow(<Discovery {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(props.deleteTutorials).toHaveBeenCalledWith([
        {
          id: 'hello',
          productOrTutoIdentifier: 'tuto_0',
        },
      ])
    })

    it('should not delete tutorials for current user', () => {
      // given
      props.tutorials = []
      const wrapper = shallow(<Discovery {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(props.deleteTutorials).not.toHaveBeenCalledWith()
    })
  })

  describe('functions', () => {
    describe('handleSuccess', () => {
      it('should reset read recommendations', () => {
        // given
        const action = {
          payload: {
            data: [{ id: 'ABC1' }],
          },
        }
        const wrapper = shallow(<Discovery {...props} />)

        // when
        wrapper.instance().handleSuccess({}, action)

        // then
        expect(props.resetReadRecommendations).toHaveBeenCalledWith()
      })

      it('should set atWorldsEnd state to true when no recommendations have been fetched', () => {
        // given
        const action = {
          payload: {
            data: [],
          },
        }
        props.recommendations = [{ id: 'ABC1' }]
        const wrapper = shallow(<Discovery {...props} />)

        // when
        wrapper.instance().handleSuccess({}, action)

        // then
        expect(wrapper.state()).toStrictEqual({
          atWorldsEnd: true,
          hasError: false,
          isEmpty: false,
          isLoading: false,
        })
      })

      it('should set atWorldsEnd state to false when recommendations have been fetched', () => {
        // given
        const action = {
          payload: {
            data: [{ id: 'DEF2' }],
          },
        }
        props.recommendations = [{ id: 'ABC1' }]
        const wrapper = shallow(<Discovery {...props} />)

        // when
        wrapper.instance().handleSuccess({}, action)

        // then
        expect(wrapper.state()).toStrictEqual({
          atWorldsEnd: false,
          hasError: false,
          isEmpty: false,
          isLoading: false,
        })
      })

      it('should set isEmpty state to true when no recommendations have been fetched and no recommendations are loaded', () => {
        // given
        const action = {
          payload: {
            data: [],
          },
        }
        props.recommendations = []
        const wrapper = shallow(<Discovery {...props} />)

        // when
        wrapper.instance().handleSuccess({}, action)

        // then
        expect(wrapper.state()).toStrictEqual({
          atWorldsEnd: true,
          hasError: false,
          isEmpty: true,
          isLoading: false,
        })
      })
    })
  })

  describe('when update', () => {
    it('should update seed last request timestamp when date is posterior to limit', () => {
      // given
      jest
        .spyOn(global.Date, 'now')
        .mockImplementationOnce(() => new Date('2019-11-20T13:00:00.000Z').valueOf())

      // when
      const wrapper = shallow(<Discovery {...props} />)
      props.location = {
        pathname: 'nouveauPath',
        search: '',
      }
      wrapper.setProps(props)

      // then
      expect(props.updateLastRequestTimestamp).toHaveBeenCalledWith()
    })

    it('should not update seed last request timestamp when date is anterior to limit', () => {
      // given
      jest
        .spyOn(global.Date, 'now')
        .mockImplementationOnce(() => new Date('2019-11-20T00:00:00.000Z').valueOf())

      // when
      const wrapper = shallow(<Discovery {...props} />)
      props.location = {
        pathname: 'nouveauPath',
        search: '',
      }
      wrapper.setProps(props)

      // then
      expect(props.updateLastRequestTimestamp).not.toHaveBeenCalledWith()
    })
  })
})
