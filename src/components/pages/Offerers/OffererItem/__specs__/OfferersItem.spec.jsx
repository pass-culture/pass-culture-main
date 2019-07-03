import React from 'react'
import { shallow } from 'enzyme'

import OffererItem from '../OffererItem'

describe('src | components | pages | Offerers | OffererItem', () => {
  let props

  beforeEach(() => {
    props = {
      venues: [],
      physicalVenues: []
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<OffererItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
