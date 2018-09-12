import React from 'react'
import { shallow } from 'enzyme'

import TermsPage from '../TermsPage'

describe('src | components | pages | TermsPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<TermsPage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
