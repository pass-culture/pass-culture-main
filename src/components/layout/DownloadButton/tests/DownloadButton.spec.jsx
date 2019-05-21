import React from 'react'
import { shallow } from 'enzyme'

import DownloadButton from '../DownloadButton'

describe('src | components | Layout | DownloadButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        downloadFileOrNotifyAnError: () => jest.fn(),
      }

      // when
      const wrapper = shallow(<DownloadButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('should set loading and disabled during onClick', done => {
      // given
      const props = {
        downloadFileOrNotifyAnError: () => jest.fn(),
      }

      // when
      const wrapper = shallow(<DownloadButton {...props} />)

      // then
      let buttonProps = wrapper.find('button[download]').props()
      expect(buttonProps.disabled).toEqual(false)
      expect(buttonProps.className.includes('is-loading')).toEqual(false)

      // when
      wrapper.find('button[download]').simulate('click')

      // then
      buttonProps = wrapper.find('button[download]').props()
      expect(buttonProps.disabled).toEqual(true)
      expect(buttonProps.className.includes('is-loading')).toEqual(true)

      // when (in the end of digest)
      setTimeout(() => {
        // then
        buttonProps = wrapper.find('button[download]').props()
        expect(buttonProps.disabled).toEqual(false)
        expect(buttonProps.className.includes('is-loading')).toEqual(false)
        done()
      })
    })
  })
})
