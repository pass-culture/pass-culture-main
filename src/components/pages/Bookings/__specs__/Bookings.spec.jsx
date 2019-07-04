import React from 'react'
import { shallow } from 'enzyme'

import Bookings from '../Bookings'
import DownloadButtonContainer from "../../../layout/DownloadButton/DownloadButtonContainer";

describe('src | components | pages | Bookings', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Bookings />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('the download button', () => {
    it('should not be visible by default', () => {
      // given
      const props = {
      }

      // when
      const wrapper = shallow(<Bookings {...props}/>)

      // then
      const downloadButton = wrapper.find(DownloadButtonContainer)
      expect(downloadButton).toHaveLength(0)
    })

    it('should use the pathToCsvFile property when displayed', () => {
      // given
      const props = {
        showDownloadButton: true,
        pathToCsvFile: '/path/to/csv/file?with=query'
      }

      // when
      const wrapper = shallow(<Bookings {...props}/>)

      // then
      const downloadButton = wrapper.find(DownloadButtonContainer)
      expect(downloadButton).toHaveLength(1)
      expect(downloadButton.prop('href')).toBe('/path/to/csv/file?with=query')
    })
  })
})
