// jest --env=jsdom ./src/components/pages/tests/TermsPage --watch
import React from 'react'
import { shallow } from 'enzyme'

import TermsPage from '../TermsPage'

describe('src | components | pages | TermsPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = { appversion: 'major.minor.patch' }
      // when
      const wrapper = shallow(<TermsPage {...props} />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
