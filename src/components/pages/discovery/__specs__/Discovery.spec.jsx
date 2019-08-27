import React from 'react'
import { shallow } from 'enzyme'

import Discovery from '../Discovery'

describe('src | components | pages | discovery | Discovery', () => {
  let props

  beforeEach(() => {
    props = {
      loadRecommendations: jest.fn(),
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {},
      },
      onRequestFailRedirectToHome: jest.fn(),
      readRecommendations: [],
      recommendations: [],
      redirectToFirstRecommendationIfNeeded: jest.fn(),
      resetReadRecommendations: jest.fn(),
      resetRecommendations: jest.fn(),
      resetRecommendationsAndBookings: jest.fn(),
      saveLoadRecommendationsTimestamp: jest.fn(),
      shouldReloadRecommendations: false,
      showPasswordChangedPopin: jest.fn(),
      withBackButton: false,
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
})
