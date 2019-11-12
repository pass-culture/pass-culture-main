import React from 'react'
import { shallow } from 'enzyme'

import Discovery from '../Discovery'

describe('src | components | pages | discovery | Discovery', () => {
  let props

  beforeEach(() => {
    props = {
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
      redirectHome: jest.fn(),
      readRecommendations: [],
      recommendations: [],
      redirectToFirstRecommendationIfNeeded: jest.fn(),
      resetReadRecommendations: jest.fn(),
      resetRecommendations: jest.fn(),
      resetRecommendationsAndBookings: jest.fn(),
      saveLastRecommendationsRequestTimestamp: jest.fn(),
      shouldReloadRecommendations: false,
      showPasswordChangedPopIn: jest.fn(),
      tutorials: [],
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Discovery {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('constructor', () => {
    it('should initialize state correctly', () => {
      // given
      const wrapper = shallow(<Discovery {...props} />)

      // then
      const expected = {
        atWorldsEnd: false,
        hasError: false,
        isEmpty: null,
        isLoading: false,
      }
      expect(wrapper.state()).toStrictEqual(expected)
    })
  })

  describe('when unmount Discovery', () => {
    it('should delete tutorials for new user', () => {
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

    it('should not delete tutorials for old user', () => {
      // given
      props.tutorials = []
      const wrapper = shallow(<Discovery {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(props.deleteTutorials).toHaveLength(0)
    })
  })
})
