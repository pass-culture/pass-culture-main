import React from 'react'
import { shallow } from 'enzyme'

import { RawMain } from '../Main'

describe('src | components | layout | Main', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: jest.fn(),
        history: {},
        location: {},
        name: 'foo',
      }

      // when
      const wrapper = shallow(
        <RawMain {...props}>
          <div>foo</div>
        </RawMain>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
