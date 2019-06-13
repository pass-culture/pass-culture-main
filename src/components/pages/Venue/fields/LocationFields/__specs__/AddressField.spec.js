import AddressField from '../AddressField'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | pages | Venue | fields | AddressField', () => {
  let props

  beforeEach(() => {
    props = {
      name: 'fake name',
      form: {}
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<AddressField {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
