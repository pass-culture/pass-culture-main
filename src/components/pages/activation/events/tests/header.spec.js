// jest --env=jsdom ./src/components/pages/activation/events/tests/header --watch
import React from 'react'
import { shallow } from 'enzyme'
import Header from '../header'

describe('src | components | pages | activation | events | Header', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Header />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
