import React from 'react'
import { shallow } from 'enzyme'

import Recto from '../Recto'

describe('src | components | recto | Recto', () => {
  describe('snapshot', () => {
    it('should match snapshot with required props only', () => {
      // given
      const props = {
        areDetailsVisible: true,
      }

      // when
      const wrapper = shallow(<Recto {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
