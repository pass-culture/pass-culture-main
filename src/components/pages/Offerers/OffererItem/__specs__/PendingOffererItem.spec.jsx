import React from 'react'
import { shallow } from 'enzyme'

import PendingOffererItem from '../PendingOffererItem'

describe('src | components | pages | Offerers | OffererItem | PendingOffererItem', () => {
  let props

  beforeEach(() => {
    props = {
      offerer: {}
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<PendingOffererItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
