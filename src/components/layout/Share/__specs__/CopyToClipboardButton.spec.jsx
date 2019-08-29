import React from 'react'
import { shallow } from 'enzyme'

import CopyToClipboardButton from '../CopyToClipboardButton'

const onClickMock = jest.fn()

describe('src | components | share | CopyToClipboardButton', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      onClick: onClickMock,
      value: 'Fake Value',
    }
    // when
    const wrapper = shallow(<CopyToClipboardButton {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
