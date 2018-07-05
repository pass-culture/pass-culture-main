import React from 'react'
import BetaPage from '../BetaPage'
import { shallow } from 'enzyme'

describe('src | components | pages | BetaPage', () => {

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {}
      }

      // when
      const wrapper = shallow(<BetaPage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
