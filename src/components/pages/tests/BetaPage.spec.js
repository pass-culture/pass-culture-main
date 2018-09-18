import React from 'react'
import { shallow } from 'enzyme'

import BetaPage from '../BetaPage'

describe('src | components | pages | BetaPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<BetaPage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
