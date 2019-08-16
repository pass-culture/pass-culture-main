import { shallow } from 'enzyme'
import React from 'react'

import Signin from '../Signin'

describe('src | components | pages | signin | Signin', () => {
  let props

  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      history: {},
      query: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Signin {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('constructor', () => {
    it('should initialize state correctly', () => {
      // given
      const wrapper = shallow(<Signin {...props} />)
      const expected = { isloading: false }

      // then
      expect(wrapper.state()).toStrictEqual(expected)
    })
  })

  describe('handleOnFormSubmit', () => {
    describe('with succes', () => {
      it('should call data reducer', () => {
        // given
        const formValues = {
          identifier: 'name@email.com',
          password: 'SomePassWord',
        }
        const wrapper = shallow(<Signin {...props} />)

        // when
        wrapper.instance().handleOnFormSubmit(formValues)
        const data = {
          config: {
            apiPath: '/users/signin',
            body: formValues,
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
            method: 'POST',
          },
          type: 'REQUEST_DATA_POST_/USERS/SIGNIN',
        }

        // then
        expect(props.dispatch).toHaveBeenCalledWith(data)
      })
    })
  })
})
