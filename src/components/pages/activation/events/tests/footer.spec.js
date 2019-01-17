// jest --env=jsdom ./src/components/pages/activation/events/tests/footer --watch
import React from 'react'
import { shallow } from 'enzyme'
import Footer from '../footer'

describe('src | components | pages | activation | events | Footer', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Footer />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
