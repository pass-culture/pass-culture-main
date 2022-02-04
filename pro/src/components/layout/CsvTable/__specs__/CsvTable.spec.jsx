import { shallow } from 'enzyme'
import React from 'react'

import HeaderContainer from '../../Header/HeaderContainer'
import Spinner from '../../Spinner'
import CsvTable from '../CsvTable'

describe('src | components | layout | CsvTable', () => {
  let props
  let dataFromCsv

  beforeEach(() => {
    props = {
      currentUser: {
        publicName: 'super nom',
      },
      downloadFileOrNotifyAnError: jest.fn(),
    }
    dataFromCsv = {
      data: [
        ['data1', 'data2'],
        ['data3', 'data4'],
      ],
      headers: ['column1', 'column2'],
    }
    props.downloadFileOrNotifyAnError.mockReturnValue(
      Promise.resolve().then(() => dataFromCsv)
    )
  })

  describe('render', () => {
    it('should render a CsvTable component with default state', () => {
      // when
      const wrapper = shallow(<CsvTable {...props} />)

      // then
      expect(wrapper.state()).toStrictEqual({
        dataFromCsv: {},
        isLoading: true,
      })
    })

    it('should render a Header component with the right props', () => {
      // when
      const wrapper = shallow(<CsvTable {...props} />)

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(1)
    })

    it('should render a Spinner component by default when CsvTable is mounted', () => {
      // when
      const wrapper = shallow(<CsvTable {...props} />)

      // then
      const spinner = wrapper.find(Spinner)
      expect(spinner).toHaveLength(1)
    })

    it('should not render a Spinner component when isLoading value from state is false', () => {
      // when
      const wrapper = shallow(<CsvTable {...props} />)
      wrapper.setState({ isLoading: false })

      // then
      const spinner = wrapper.find(Spinner)
      expect(spinner).toHaveLength(0)
    })

    it('should open a new window for printing when clicking on print button', () => {
      // given
      jest.spyOn(global, 'print').mockImplementation()
      const wrapper = shallow(<CsvTable {...props} />)
      wrapper.setState({
        dataFromCsv: dataFromCsv,
        isLoading: false,
      })
      const printButton = wrapper.find('#csv-print-button')

      // then
      printButton.simulate('click')

      // then
      expect(global.print).toHaveBeenCalledWith()
    })

    it('should display a message when there is no data to display and isLoading value from state is false', () => {
      // when
      const wrapper = shallow(<CsvTable {...props} />)
      wrapper.setState({
        dataFromCsv: {},
        isLoading: false,
      })

      // then
      const noDataContainer = wrapper.find('.no-data-container')
      expect(noDataContainer).toHaveLength(1)
      expect(noDataContainer.text()).toBe('Il n’y a pas de données à afficher.')
    })

    it('should load data from csv when CsvTable component is mounted', async () => {
      // when
      const wrapper = await shallow(<CsvTable {...props} />)

      // then
      expect(props.downloadFileOrNotifyAnError).toHaveBeenCalledWith()
      expect(wrapper.state()).toStrictEqual({
        dataFromCsv: {
          data: [
            ['data1', 'data2'],
            ['data3', 'data4'],
          ],
          headers: ['column1', 'column2'],
        },
        isLoading: false,
      })
    })

    describe('when data from csv is provided and isLoading value from state is false', () => {
      it('should render a table header with 2 columns', () => {
        // when
        const wrapper = shallow(<CsvTable {...props} />)
        wrapper.setState({
          dataFromCsv: dataFromCsv,
          isLoading: false,
        })

        // then
        const thElements = wrapper.find('thead tr th')
        expect(thElements).toHaveLength(2)
      })

      it('should render a tbody with two lines', () => {
        // when
        const wrapper = shallow(<CsvTable {...props} />)
        wrapper.setState({
          dataFromCsv: dataFromCsv,
          isLoading: false,
        })

        // then
        const trElements = wrapper.find('tbody tr')
        const firstTrElement = trElements.at(0).find('td')
        const secondTrElement = trElements.at(1).find('td')
        expect(trElements).toHaveLength(2)
        expect(firstTrElement).toHaveLength(2)
        expect(firstTrElement.at(0).text()).toBe('data1')
        expect(firstTrElement.at(1).text()).toBe('data2')
        expect(secondTrElement).toHaveLength(2)
        expect(secondTrElement.at(0).text()).toBe('data3')
        expect(secondTrElement.at(1).text()).toBe('data4')
      })

      it('should render a print button with the right props', () => {
        // when
        const wrapper = shallow(<CsvTable {...props} />)
        wrapper.setState({
          dataFromCsv: dataFromCsv,
          isLoading: false,
        })

        // then
        const printButton = wrapper.find('#csv-print-button')
        expect(printButton).toHaveLength(1)
        expect(printButton.prop('className')).toBe('button is-primary')
        expect(printButton.prop('onClick')).toStrictEqual(expect.any(Function))
        expect(printButton.text()).toBe('Imprimer')
      })
    })
  })
})
