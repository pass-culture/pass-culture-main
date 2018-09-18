import React from 'react'
import { shallow } from 'enzyme'

import TermsPage from '../TermsPage'
import { version } from '../../../../package.json'

describe('src | components | pages | TermsPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        appversion: version,
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
