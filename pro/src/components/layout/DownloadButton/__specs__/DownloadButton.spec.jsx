import { shallow } from 'enzyme'
import React from 'react'

import DownloadButton from '../DownloadButton'

describe('src | components | Layout | DownloadButton', () => {
  describe('render', () => {
    it('should set loading and disabled during onClick', async () => {
      await new Promise(resolve => {
        // given
        const props = {
          children: 'Fake title',
          downloadFileOrNotifyAnError: () => jest.fn(),
        }

        // when
        const wrapper = shallow(<DownloadButton {...props} />)

        // then
        let buttonProps = wrapper.find('button[download]').props()
        expect(buttonProps.disabled).toBe(false)
        expect(buttonProps.className).not.toContain('is-loading')

        // when
        wrapper.find('button[download]').simulate('click')

        // then
        buttonProps = wrapper.find('button[download]').props()
        expect(buttonProps.disabled).toBe(true)
        expect(buttonProps.className).toContain('is-loading')

        // when (in the end of digest)
        setTimeout(() => {
          // then
          buttonProps = wrapper.find('button[download]').props()
          expect(buttonProps.disabled).toBe(false)
          expect(buttonProps.className).not.toContain('is-loading')
          resolve()
        })
      })
    })
  })
})
