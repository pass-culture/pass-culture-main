import React from 'react'
import { shallow } from 'enzyme'
import MediationItem from '../MediationItem'

describe('src | components | pages | Offer | MediationItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<MediationItem {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
