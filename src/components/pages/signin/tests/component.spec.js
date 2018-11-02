import React from 'react'
import { shallow } from 'enzyme'

import Signin from '../component'

describe('src | components | pages | signin | component', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: jest.fn(),
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
          dispatch: jest.fn(),
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
      // given
      const props = {
        dispatch: jest.fn(),
        history: {},
      }

      // when
      const wrapper = shallow(<Signin {...props} />)
      // const submit = wrapper.find('Form')
      console.log('wrapper', wrapper)

      const formValue = {}
      wrapper.instance().onFormSubmit(formValue)

      // https://redux.js.org/recipes/writingtests
      console.log('state', wrapper.state())

      // expect(wrapper.children.props().onSubmit()).toHaveBeenCalledWith('totot')
    })
  })
})
