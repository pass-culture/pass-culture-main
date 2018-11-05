import React from 'react'
import { shallow } from 'enzyme'

import SharePopin from '../SharePopin'

describe.skip('src | components | share | SharePopin', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        className: 'fake-class',
        onClick: jest.fn(),
        value: 'Fake Value',
      }
      // when
      const wrapper = shallow(<SharePopin {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
