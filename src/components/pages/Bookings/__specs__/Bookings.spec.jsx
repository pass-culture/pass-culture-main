import React from 'react'
import { shallow } from 'enzyme'

import Bookings from '../Bookings'
import DownloadButtonContainer from '../../../layout/DownloadButton/DownloadButtonContainer'
import CsvTableButtonContainer from '../../../layout/CsvTableButton/CsvTableButtonContainer'
import FilterByOfferContainer from '../FilterByOffer/FilterByOfferContainer'

describe('src | components | pages | Bookings', () => {
  let props

  beforeEach(() => {
    props = {
      showButtons: false,
      showOfferSection: false,
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
    it('should render a Bookings component with default props', () => {
      // when
      const wrapper = shallow(<Bookings />)

      // then
      expect(wrapper.prop('pathToCsvFile')).toBe()
      expect(wrapper.prop('showButtons')).toBe()
      expect(wrapper.prop('showOfferSection')).toBe()
    })

    describe('the download and display section', () => {
      it('should not render a DownloadButtonContainer component when showButtons is false', () => {
        // when
        const wrapper = shallow(<Bookings {...props} />)

        // then
        const downloadButton = wrapper.find(DownloadButtonContainer)
        expect(downloadButton).toHaveLength(0)
      })

      it('should render a DownloadButtonContainer component with the right props when showButtons is true', () => {
        // given
        props.showButtons = true

        // when
        const wrapper = shallow(<Bookings {...props} />)

        // then
        const downloadButton = wrapper.find(DownloadButtonContainer)
        expect(downloadButton).toHaveLength(1)
        expect(downloadButton.prop('href')).toBe('/path/to/csv/file?with=query')
      })

      it('should not render a CsvTableButtonContainer by default', () => {
        // when
        const wrapper = shallow(<Bookings {...props} />)

        // then
        const displayButton = wrapper.find(CsvTableButtonContainer)
        expect(displayButton).toHaveLength(0)
      })

      it('should render CsvTableButtonContainer with the right props when displayed', () => {
        // given
        props.showButtons = true

        // when
        const wrapper = shallow(<Bookings {...props} />)

        // then
        const displayButton = wrapper.find(CsvTableButtonContainer)
        expect(displayButton).toHaveLength(1)
        expect(displayButton.prop('href')).toBe('/path/to/csv/file?with=query')
      })
    })

  describe('the offer section', () => {
      it('should not render a FilterByOfferContainer component when showOfferSection is false', () => {
        // given
        props.showOfferSection = false

        // when
        const wrapper = shallow(<Bookings {...props} />)

        // then
        const filterByOfferContainer = wrapper.find(FilterByOfferContainer)
        expect(filterByOfferContainer).toHaveLength(0)
      })

      it('should render a FilterByOfferContainer component when showOfferSection is true', () => {
        // given
        props.showOfferSection = true

        //when
        const wrapper = shallow(<Bookings {...props} />)

        // then
        const filterByOfferContainer = wrapper.find(FilterByOfferContainer)
        expect(filterByOfferContainer).toHaveLength(1)
      })
    })
  })
})
