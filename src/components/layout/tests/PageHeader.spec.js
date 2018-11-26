// jest --env=jsdom ./src/components/layout/tests/PageHeader --watch
import React from 'react'
import { shallow } from 'enzyme'

import PageHeader from '../PageHeader'

describe('src | components | pages | PageHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        title: 'fake title',
      }

      // when
      const wrapper = shallow(<PageHeader {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
