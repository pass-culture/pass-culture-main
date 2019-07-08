import React from 'react'
import { shallow } from 'enzyme'

import BackLink from '../../../layout/Header/BackLink'
import Discovery from '../Discovery'

describe('src | components | pages | discovery | Discovery', () => {
  let props

  beforeEach(() => {
    props = {
      backLink: true,
      dispatch: jest.fn(),
      fromPassword: true,
      history: {},
      loadRecommendations: jest.fn(),
      location: {
        search: '',
      },
      match: {
        params: {},
      },
      onRequestFailRedirectToHome: jest.fn(),
      recommendations: [],
      redirectToFirstRecommendationIfNeeded: jest.fn(),
      resetReadRecommendations: jest.fn(),
      resetRecommendations: jest.fn(),
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
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  xdescribe('constructor', () => {
    it('should initialize state correctly', () => {
      // given
      const wrapper = shallow(<Discovery {...props} />)

      // then
      const expected = {
        atWorldsEnd: false,
        hasError: false,
        isEmpty: null,
        isLoading: true,
      }
      expect(wrapper.state()).toStrictEqual(expected)
    })
  })

  xdescribe('handleDataRequest', () => {
    describe('One case', () => {
      it('should update recommendation infos using API when Main component is rendered', () => {
        // given
        shallow(<Discovery {...props} />)

        // then
        const expectedRequestDataAction = {
          config: {
            apiPath: '/recommendations?',
            body: {
              readRecommendations: null,
              seenRecommendationIds: null,
            },
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
            method: 'PUT',
            normalizer: {
              bookings: 'bookings',
            },
          },
          type: 'REQUEST_DATA_PUT_/RECOMMENDATIONS?',
        }
        expect(props.dispatch.mock.calls).toHaveLength(1)
        expect(props.dispatch.mock.calls[0][0]).toStrictEqual(expectedRequestDataAction)
      })
    })
  })

  describe('render()', () => {
    it('should display the back button when I am on the back of an offer', () => {
      // given
      props.match.params.view = 'verso'
      const wrapper = shallow(<Discovery {...props} />)

      // when
      const backLink = wrapper.find(BackLink)

      // then
      expect(backLink).toHaveLength(1)
    })
  })
})
