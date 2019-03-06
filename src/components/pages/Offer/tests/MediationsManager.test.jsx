import React from 'react'
import { shallow } from 'enzyme'
import MediationsManager from '../MediationsManager'

describe('src | components | pages | Offer | MediationsManager', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<MediationsManager {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
