import React from 'react'
import { shallow } from 'enzyme'

import CsvDetailView from '../CsvDetailView'
import Header from '../../Header/Header'

describe('src | components | Layout | CsvDetailView', () => {
  let props

  beforeEach(() => {
    props = {
      currentUser: {
        publicName: 'super nom',
      },
      location: {
        state: {
          data: [['data1', 'data2'], ['data3', 'data4']],
          headers: ['column1', 'column2'],
        },
      },
    }
    jest.spyOn(global, 'print')
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<CsvDetailView {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a Header component with the right props', () => {
    // when
    const wrapper = shallow(<CsvDetailView {...props} />)

    // then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('name')).toBe('super nom')
    expect(header.prop('offerers')).toStrictEqual([])
  })

  it('should render a table header with 2 columns when csv contains 2 elements in header', () => {
    // when
    const wrapper = shallow(<CsvDetailView {...props} />)

    // then
    const thElements = wrapper.find('thead tr th')
    expect(thElements).toHaveLength(2)
  })

  it('should render a tbody with two lines, containing two columns when csv containes 2 elements in headers and 2 lines of data', () => {
    // when
    const wrapper = shallow(<CsvDetailView {...props} />)

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
    const wrapper = shallow(<CsvDetailView {...props} />)

    // then
    const printButton = wrapper.find('#csv-print-button')
    expect(printButton).toHaveLength(1)
    expect(printButton.prop('className')).toBe('button is-primary')
    expect(printButton.prop('onClick')).toStrictEqual(expect.any(Function))
    expect(printButton.text()).toBe('Imprimer')
  })

  it('should open a new window for printing when clicking on print button', () => {
    // given
    const wrapper = shallow(<CsvDetailView {...props} />)
    const printButton = wrapper.find('#csv-print-button')

    // then
    printButton.simulate('click')

    // then
    expect(global.print).toHaveBeenCalledWith()
  })
})
