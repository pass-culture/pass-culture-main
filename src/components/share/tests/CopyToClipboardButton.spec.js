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
  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // given
        const props = {
          onClick: onClickMock,
          value: 'Fake Value',
        }

        // when
        const wrapper = shallow(<CopyToClipboardButton {...props} />)
        const expected = {
          copied: false,
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })
    describe('onCopy', () => {
      it('should change copied state to true', () => {
        // given
        const props = {
          onClick: onClickMock,
          value: 'Fake Value',
        }

        // when
        const wrapper = shallow(<CopyToClipboardButton {...props} />)
        wrapper.props().onCopy()
        const expected = {
          copied: true,
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })
  })
})
