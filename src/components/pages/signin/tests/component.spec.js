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
      it('should initialize state with functions', () => {
        // given
        const props = {
          dispatch: jest.fn(),
          history: {},
        }

        // when
        const wrapper = shallow(<Signin {...props} />)

        // then
        expect(wrapper.state()).toEqual({ isloading: false })
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
      wrapper.instance().onFormSubmit('formValues')
      // const expected = 'some thing'

      // then

      // expected
      // state qui change
      // request Data
    })
  })
})
