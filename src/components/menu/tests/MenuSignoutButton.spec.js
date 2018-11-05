import React from 'react'
import { shallow } from 'enzyme'

import MenuSignoutButton from '../MenuSignoutButton'

describe('src | components | menu | MenuSignoutButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: jest.fn(),
        history: true,
      }

      // when
      const wrapper = shallow(<MenuSignoutButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
