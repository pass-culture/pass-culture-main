import React from 'react'
import { shallow } from 'enzyme'

import DownloadButton from '../DownloadButton'

describe('src | components | Layout | DownloadButton', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      children: 'Fake title',
      downloadFileOrNotifyAnError: () => jest.fn(),
    }

    // when
    const wrapper = shallow(<DownloadButton {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should set loading and disabled during onClick', () => {
      return new Promise(done => {
        // given
        const props = {
          children: 'Fake title',
          downloadFileOrNotifyAnError: () => jest.fn(),
        }

        // when
        const wrapper = shallow(<DownloadButton {...props} />)

        // then
        let buttonProps = wrapper.find('button[download]').props()
        expect(buttonProps.disabled).toStrictEqual(false)
        expect(buttonProps.className).not.toContain('is-loading')

        // when
        wrapper.find('button[download]').simulate('click')

        // then
        buttonProps = wrapper.find('button[download]').props()
        expect(buttonProps.disabled).toStrictEqual(true)
        expect(buttonProps.className).toContain('is-loading')

        // when (in the end of digest)
        setTimeout(() => {
          // then
          buttonProps = wrapper.find('button[download]').props()
          expect(buttonProps.disabled).toStrictEqual(false)
          expect(buttonProps.className).not.toContain('is-loading')
          done()
        })
      })
    })
  })
})
