import { shallow } from 'enzyme'
import React from 'react'

import Signin from '../Signin'

const dispatchMock = jest.fn()

describe('src | components | pages | signin | component', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: dispatchMock,
        history: {},
      }

      // when
      const wrapper = shallow(<Signin {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // given
        const props = {
          dispatch: dispatchMock,
          history: {},
        }

        // when
        const wrapper = shallow(<Signin {...props} />)
        const expected = { isloading: false }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })

    describe('onFormSubmit', () => {
      describe('with succes', () => {
        it('should call data reducer', () => {
          // given
          const props = {
            dispatch: dispatchMock,
            history: {},
          }
          const formValues = {
            identifier: 'name@email.com',
            password: 'SomePassWord',
          }

          // when
          const wrapper = shallow(<Signin {...props} />)
          wrapper.instance().handleRequestFail = jest.fn()
          wrapper.instance().handleRequestSuccess = jest.fn()

          wrapper.instance().onFormSubmit(formValues)

          const data = {
            config: {
              apiPath: '/users/signin',
              body: formValues,
              handleFail: undefined,
              handleSuccess: undefined,
              method: 'POST',
            },
            type: 'REQUEST_DATA_POST_/USERS/SIGNIN',
          }
          // then
          expect(dispatchMock).toHaveBeenCalledWith(data)
        })
      })
    })
  })
})
