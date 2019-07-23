import React from 'react'
import { shallow } from 'enzyme'

import Bookings from '../Bookings'
import DownloadButtonContainer from '../../../layout/DownloadButton/DownloadButtonContainer'
import DisplayButtonContainer from '../../../layout/CsvTableButton/CsvTableButtonContainer'

describe('src | components | pages | Bookings', () => {
  let props

  beforeEach(() => {
    props = {
      showButtons: false,
      pathToCsvFile: '/path/to/csv/file?with=query',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Bookings />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should not render a download button by default', () => {
      // when
      const wrapper = shallow(<Bookings {...props} />)

      // then
      const downloadButton = wrapper.find(DownloadButtonContainer)
      expect(downloadButton).toHaveLength(0)
    })

    it('should render a download button with the right props when displayed', () => {
      // given
      props.showButtons = true

      // when
      const wrapper = shallow(<Bookings {...props} />)

      // then
      const downloadButton = wrapper.find(DownloadButtonContainer)
      expect(downloadButton).toHaveLength(1)
      expect(downloadButton.prop('href')).toBe('/path/to/csv/file?with=query')
    })

    it('should not render a display button by default', () => {
      // when
      const wrapper = shallow(<Bookings {...props} />)

      // then
      const displayButton = wrapper.find(DisplayButtonContainer)
      expect(displayButton).toHaveLength(0)
    })

    it('should render a display button with the right props when displayed', () => {
      // given
      props.showButtons = true

      // when
      const wrapper = shallow(<Bookings {...props} />)

      // then
      const displayButton = wrapper.find(DisplayButtonContainer)
      expect(displayButton).toHaveLength(1)
      expect(displayButton.prop('href')).toBe('/path/to/csv/file?with=query')
    })
  })
})
