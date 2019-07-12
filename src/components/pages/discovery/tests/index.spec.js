import React from 'react'
import { shallow } from 'enzyme'

import { RawDiscoveryPage } from '../index'
import BackLink from '../../../layout/Header/BackLink'

describe('src | components | pages | discovery | RawDiscoveryPage', () => {
  let props

  beforeEach(() => {
    props = {
      backLink: true,
      dispatch: jest.fn(),
      fromPassword: true,
      history: {},
      location: {
        search: '',
      },
      match: {
        params: {},
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<RawDiscoveryPage {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('constructor', () => {
    it('should initialize state correctly', () => {
      // given
      const wrapper = shallow(<RawDiscoveryPage {...props} />)

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

  describe('handleDataRequest', () => {
    describe('one case', () => {
      it('should update recommendation infos using API when Main component is rendered', () => {
        // given
        shallow(<RawDiscoveryPage {...props} />)

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
      const wrapper = shallow(<RawDiscoveryPage {...props} />)

      // when
      const backLink = wrapper.find(BackLink)

      // then
      expect(backLink).toHaveLength(1)
    })
  })
})
