import { shallow } from 'enzyme'
import React from 'react'

import withNotRequiredLogin, { handleSuccess } from '../withNotRequiredLogin'
import { getRedirectToCurrentLocationOrDiscovery } from '../helpers'

jest.mock('../helpers')

const Test = () => null
const NotRequiredLoginTest = withNotRequiredLogin(Test)

describe('src | components | pages | hocs | with-login | withNotRequiredLogin', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<NotRequiredLoginTest />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('handleSuccess()', () => {
    it('should call getRedirectToCurrentLocationOrDiscovery with right parameters', () => {
      // given
      const state = {}
      const action = {
        payload: {
          datum: {
            email: 'michel.marx@youpi.fr',
            needsToFillCulturalSurvey: false
          }
        }
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {
          hash: "",
          key: expect.any(String),
          pathname: "/test",
          search: "",
          state: undefined
        },
      }

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(getRedirectToCurrentLocationOrDiscovery).toHaveBeenCalledWith({
        currentUser: {
          email: 'michel.marx@youpi.fr',
          needsToFillCulturalSurvey: false,
        },
        hash: '',
        key: expect.any(String),
        pathname: '/test',
        search: '',
        state: undefined,
      })
    })

    it('should not call push history when user is redirected', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrDiscovery.mockReturnValue('/fake-url')

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).toHaveBeenCalledWith('/fake-url')
    })

    it('should call push history when its success', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrDiscovery.mockReturnValue(undefined)

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).not.toHaveBeenCalled()
    })
  })
})
