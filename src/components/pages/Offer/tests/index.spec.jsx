import React from 'react'
import { shallow } from 'enzyme'

import Offer from '../index'

describe('src | components | pages | Offer | Offer ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<Offer {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
