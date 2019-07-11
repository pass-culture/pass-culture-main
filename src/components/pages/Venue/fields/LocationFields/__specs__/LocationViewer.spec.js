import { shallow } from 'enzyme'
import LocationViewer from '../LocationViewer'
import React from 'react'

describe('src | components | pages | Venue | fields | LocationViewer', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<LocationViewer />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
