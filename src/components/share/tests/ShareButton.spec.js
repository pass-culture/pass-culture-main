import React from 'react'
import { shallow } from 'enzyme'

import ShareButton from '../ShareButton'

describe.skip('src | components | share | ShareButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        className: 'fake-class',
        onClick: jest.fn(),
        value: 'Fake Value',
      }
      // when
      const wrapper = shallow(<ShareButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
