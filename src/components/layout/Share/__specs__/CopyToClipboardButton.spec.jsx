import { mount } from 'enzyme'
import React from 'react'
import { CopyToClipboard } from 'react-copy-to-clipboard'

import CopyToClipboardButton from '../CopyToClipboardButton'

describe('src | components | CopyToClipboardButton', () => {
  it('should display a button', () => {
    // given
    const props = {
      onClick: jest.fn(),
      value: 'Fake value',
    }
    // when
    const wrapper = mount(<CopyToClipboardButton {...props} />)

    // then
    const copyToClipboard = wrapper.find(CopyToClipboard)
    const button = wrapper.find('button').find({ children: 'Copier le lien' })
    expect(copyToClipboard.prop('onCopy')).toStrictEqual(expect.any(Function))
    expect(copyToClipboard.prop('text')).toBe('Fake value')
    expect(button).toHaveLength(1)
  })
})
