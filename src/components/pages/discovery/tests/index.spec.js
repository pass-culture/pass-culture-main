import React from 'react'
import { shallow } from 'enzyme'

import { RawDiscoveryPage } from '../index'

describe('src | components | pages | discovery | Index | DiscoveryPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        backButton: true,
        dispatch: jest.fn(),
        history: {},
        location: {
          search: '',
        },
        match: {},
      }

      // when
      const wrapper = shallow(<RawDiscoveryPage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('function', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // given
        const props = {
          backButton: true,
          dispatch: jest.fn(),
          history: {},
          location: {
            search: '',
          },
          match: {},
        }

        // when
        const wrapper = shallow(<RawDiscoveryPage {...props} />)
        const expected = {
          haserror: false,
          isempty: false,
          isloading: true,
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })

    describe('handleDataRequest', () => {
      describe('One case', () => {
        it('should first dispatch requestData when  Main component is rendered', () => {
          // given
          const dispatchMock = jest.fn()
          const props = {
            backButton: true,
            dispatch: dispatchMock,
            history: {},
            location: {
              search: '',
            },
            match: {},
          }

          // when
          shallow(<RawDiscoveryPage {...props} />)
          const expectedRequest = {
            config: {},
            method: 'PUT',
            path: 'recommendations?',
            type: 'REQUEST_DATA_PUT_RECOMMENDATIONS?',
          }

          // THEN
          expect(dispatchMock.mock.calls.length).toBe(1)
          expect(dispatchMock.mock.calls[0][0].method).toEqual(
            expectedRequest.method
          )
        })
      })
    })
  })
})
