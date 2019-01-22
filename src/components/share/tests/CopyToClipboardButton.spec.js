import React from 'react'
import { shallow } from 'enzyme'

import CopyToClipboardButton from '../CopyToClipboardButton'

const onClickMock = jest.fn()

describe('src | components | share | CopyToClipboardButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        onClick: onClickMock,
        value: 'Fake Value',
      }
      // when
      const wrapper = shallow(<CopyToClipboardButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
