import { shallow } from 'enzyme'
import React from 'react'

import Signin from '../Signin'

describe('src | components | pages | signin | Signin', () => {
  let props

  beforeEach(() => {
    props = {
      submitSigninForm: jest.fn(),
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

  describe('handleOnFormSubmit', () => {
    it('should set isLoading state to true', () => {
      // given
      const formValues = {
        identifier: 'name@email.com',
        password: 'SomePassWord',
      }
      const wrapper = shallow(<Signin {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      expect(wrapper.state()).toStrictEqual({
        isLoading: true,
      })
    })

    it('should call submitSigninForm from container', () => {
      // given
      const formValues = {
        identifier: 'name@email.com',
        password: 'SomePassWord',
      }
      const wrapper = shallow(<Signin {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      expect(props.submitSigninForm).toHaveBeenCalledWith(
        formValues,
        wrapper.instance().handleRequestFail,
        wrapper.instance().handleRequestSuccess
      )
    })
  })
})
