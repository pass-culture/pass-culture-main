import React from 'react'
import { shallow } from 'enzyme'
import FilterByDate from '../FilterByDate'

describe('src | components | pages | FilterByDate | FilterByDate', () => {
  let props

  beforeEach(() => {
    props = {
      updateBookingsFrom: jest.fn(),
      updateBookingsTo: jest.fn(),
      showEventDateSection: false,
      showThingDateSection: false,
      stocks: [
        { beginningDatetime: '2019-07-28T21:59:00Z' },
        { beginningDatetime: '2019-08-16T21:59:00Z' },
      ],
      departementCode: '75',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<FilterByDate {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('when showThingDateSection is true', () => {
      it('should display the proper label for bookings in a specific period', () => {
        // given
        props.showThingDateSection = true

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const filterThingByDate = wrapper.find('div').at(1)
        expect(filterThingByDate.text()).toBe('Effectuées en :')
      })

      it('should display the proper label for month selection', () => {
        // given
        props.showThingDateSection = true

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const monthLabel = wrapper.find('label').at(0)
        expect(monthLabel.prop('className')).toBe('is-invisible')
        expect(monthLabel.prop('htmlFor')).toBe('month')
        expect(monthLabel.text()).toBe('Sélectionnez le mois.')
      })

      it('should display the proper label for year selection', () => {
        // given
        props.showThingDateSection = true

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const yearLabel = wrapper.find('label').at(1)
        expect(yearLabel.prop('className')).toBe('is-invisible')
        expect(yearLabel.prop('htmlFor')).toBe('year')
        expect(yearLabel.text()).toStrictEqual("Sélectionnez l'année.")
      })

      it('should render a select input for month with 13 options', () => {
        // given
        props.showThingDateSection = true

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const selectMonth = wrapper.find('#month')
        expect(selectMonth.prop('className')).toBe('pc-selectbox')
        expect(selectMonth.prop('id')).toBe('month')
        expect(selectMonth.prop('onBlur')).toStrictEqual(expect.any(Function))
        expect(selectMonth.prop('onChange')).toStrictEqual(expect.any(Function))
        const options = selectMonth.find('option')
        expect(options).toHaveLength(13)
        expect(options.at(0).prop('disabled')).toBe(true)
        expect(options.at(0).prop('label')).toBe(' - Mois - ')
        expect(options.at(0).prop('selected')).toBe(true)
        expect(options.at(1).key()).toBe('janvier')
        expect(options.at(1).prop('value')).toBe(0)
        expect(options.at(2).key()).toBe('février')
        expect(options.at(2).prop('value')).toBe(1)
        expect(options.at(3).key()).toBe('mars')
        expect(options.at(3).prop('value')).toBe(2)
        expect(options.at(4).key()).toBe('avril')
        expect(options.at(4).prop('value')).toBe(3)
        expect(options.at(5).key()).toBe('mai')
        expect(options.at(5).prop('value')).toBe(4)
        expect(options.at(6).key()).toBe('juin')
        expect(options.at(6).prop('value')).toBe(5)
        expect(options.at(7).key()).toBe('juillet')
        expect(options.at(7).prop('value')).toBe(6)
        expect(options.at(8).key()).toBe('août')
        expect(options.at(8).prop('value')).toBe(7)
        expect(options.at(9).key()).toBe('septembre')
        expect(options.at(9).prop('value')).toBe(8)
        expect(options.at(10).key()).toBe('octobre')
        expect(options.at(10).prop('value')).toBe(9)
        expect(options.at(11).key()).toBe('novembre')
        expect(options.at(11).prop('value')).toBe(10)
        expect(options.at(12).key()).toBe('décembre')
        expect(options.at(12).prop('value')).toBe(11)
      })
    })

    describe('when showEventDateSection is true', () => {
      it('should display the proper label for date selection', () => {
        // given
        props.showEventDateSection = true

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const labels = wrapper.find('div').find('label')
        expect(labels.at(0).text()).toBe('Pour la date du :')
      })

      it('should render a select input for date with 3 options', () => {
        // given
        props.showEventDateSection = true
        props.stocks = [
          { beginningDatetime: '2019-02-28T21:59:00Z' },
          { beginningDatetime: '2019-08-16T21:59:00Z' },
        ]

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const selectDate = wrapper.find('#event-date')
        expect(selectDate.prop('className')).toBe('pc-selectbox')
        expect(selectDate.prop('id')).toBe('event-date')
        expect(selectDate.prop('onBlur')).toStrictEqual(expect.any(Function))
        expect(selectDate.prop('onChange')).toStrictEqual(expect.any(Function))
        const options = selectDate.find('option')
        expect(options).toHaveLength(3)
        expect(options.at(0).prop('disabled')).toBe(true)
        expect(options.at(0).prop('label')).toBe(' - Choisissez une date - ')
        expect(options.at(0).prop('selected')).toBe(true)
        expect(options.at(1).key()).toBe('2019-02-28T21:59:00Z')
        expect(options.at(1).prop('value')).toBe('2019-02-28T21:59:00Z')
        expect(options.at(1).text()).toBe('jeudi 28 février 2019, 22:59')
        expect(options.at(2).key()).toBe('2019-08-16T21:59:00Z')
        expect(options.at(2).prop('value')).toBe('2019-08-16T21:59:00Z')
        expect(options.at(2).text()).toBe('vendredi 16 août 2019, 23:59')
      })

      it('should render a select input for date with correct timezone', () => {
        // given
        props.showEventDateSection = true
        props.stocks = [
          { beginningDatetime: '2019-02-28T21:59:00Z' },
          { beginningDatetime: '2019-08-16T18:59:00Z' },
        ]
        props.departementCode = '973'

        // when
        const wrapper = shallow(<FilterByDate {...props} />)

        // then
        const selectDate = wrapper.find('#event-date')
        const options = selectDate.find('option')
        expect(options.at(1).text()).toBe('jeudi 28 février 2019, 18:59')
        expect(options.at(2).text()).toBe('vendredi 16 août 2019, 15:59')
      })
    })
  })

  describe('handleOnChangeMonth', () => {
    it('should update month from state when month is selected', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selectMonthInput = wrapper.find('#month')

      // when
      selectMonthInput.simulate('change', { target: { value: 3 } })

      // then
      expect(wrapper.state('month')).toBe(3)
    })

    it('should not update bookingsFrom from store when month is provided but not year', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selectMonthInput = wrapper.find('#month')

      // when
      selectMonthInput.simulate('change', { target: { value: 3 } })

      // then
      expect(props.updateBookingsFrom).not.toHaveBeenCalled()
    })

    it('should not update bookingsTo from store when month is provided but not year', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selectMonthInput = wrapper.find('#month')

      // when
      selectMonthInput.simulate('change', { target: { value: 3 } })

      // then
      expect(props.updateBookingsTo).not.toHaveBeenCalled()
    })

    it('should update bookingsTo & bookingsFrom from store when month & year are provided', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      wrapper.setState({ year: '2018' })
      const selectMonthInput = wrapper.find('#month')

      // when
      selectMonthInput.simulate('change', { target: { value: 3 } })

      // then
      expect(props.updateBookingsFrom).toHaveBeenCalledWith('2018-04-01T00:00:00Z')
      expect(props.updateBookingsTo).toHaveBeenCalledWith('2018-04-30T23:59:59Z')
    })
  })

  describe('handleOnChangeYear', () => {
    it('should update year from state when year is selected', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selectYearInput = wrapper.find('#year')

      // when
      selectYearInput.simulate('change', { target: { value: '2018' } })

      // then
      expect(wrapper.state('year')).toBe('2018')
    })

    it('should not update bookingsFrom from store when year is provided but not month', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selectYearInput = wrapper.find('#year')

      // when
      selectYearInput.simulate('change', { target: { value: '2018' } })

      // then
      expect(props.updateBookingsFrom).not.toHaveBeenCalled()
    })

    it('should not update bookingsTo from store when year is provided but not month', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selectYearInput = wrapper.find('#year')

      // when
      selectYearInput.simulate('change', { target: { value: '2018' } })

      // then
      expect(props.updateBookingsTo).not.toHaveBeenCalled()
    })

    it('should update bookingsFrom & bookingsTo from store when month & year are provided', () => {
      // given
      props.showThingDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      wrapper.setState({ month: 3 })
      const selectYearInput = wrapper.find('#year')

      // when
      selectYearInput.simulate('change', { target: { value: '2018' } })

      // then
      expect(props.updateBookingsFrom).toHaveBeenCalledWith('2018-04-01T00:00:00Z')
      expect(props.updateBookingsTo).toHaveBeenCalledWith('2018-04-30T23:59:59Z')
    })
  })

  describe('handleOnChangeEventDate', () => {
    it('should update bookingsTo & bookingsFrom from store using date from select', () => {
      // given
      props.showEventDateSection = true
      const wrapper = shallow(<FilterByDate {...props} />)
      const selecteventDateInput = wrapper.find('#event-date')

      // when
      selecteventDateInput.simulate('change', { target: { value: '2019-07-28T21:59:00Z' } })

      // then
      expect(props.updateBookingsFrom).toHaveBeenCalledWith('2019-07-28T21:59:00Z')
      expect(props.updateBookingsTo).toHaveBeenCalledWith('2019-07-28T21:59:00Z')
    })
  })
})
