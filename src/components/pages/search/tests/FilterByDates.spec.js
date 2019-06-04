import { shallow } from 'enzyme'
import React from 'react'

import { DatePickerField } from '../../../forms/inputs'
import FilterByDates, { isDaysChecked } from '../FilterByDates'
import { DAYS_CHECKBOXES } from '../utils'

describe('src | components | pages | search | FilterByDates', () => {
  const fakeMethod = jest.fn()
  let props

  beforeEach(() => {
    props = {
      filterActions: {
        add: fakeMethod,
        change: fakeMethod,
        remove: fakeMethod,
      },
      filterState: {
        isNew: false,
        params: {
          categories: null,
          date: null,
          distance: null,
          jours: null,
          latitude: null,
          longitude: null,
          'mots-cles': null,
          orderBy: 'offer.id+desc',
        },
      },
      initialDateParams: false,
    }
  })

  it('should match the snapshot', () => {
    // given
    const snapshotDate = new Date('2019-06-02T12:41:33.680Z')
    global.Date = jest.fn(() => snapshotDate)

    // when
    const wrapper = shallow(<FilterByDates {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('isDaysChecked()', () => {
    describe('date is picked in calendar', () => {
      it('should not check date', () => {
        // given
        const pickedDate = new Date()

        // when
        const result = isDaysChecked(pickedDate)

        // then
        expect(result).toEqual(false)
      })
    })

    describe('date is picked with a checkbox', () => {
      it('should ckeck boxes', () => {
        // given
        const pickedDate = null
        const pickedDaysInQuery = '0-1,5-10000'
        const inputValue = '0-1'

        // when
        const result = isDaysChecked(pickedDate, pickedDaysInQuery, inputValue)

        // then
        expect(result).toEqual(true)
      })

      it('should not ckeck box', () => {
        // given
        const pickedDate = null
        const pickedDaysInQuery = '1-5'
        const inputValue = '0-1'

        // when
        const result = isDaysChecked(pickedDate, pickedDaysInQuery, inputValue)

        // then
        expect(result).toEqual(false)
      })
    })
  })

  describe('onChangePickedDate()', () => {
    it('should call change filter action function with a date', () => {
      // given
      props.filterState.params.date = '2018-10-24T09:15:55.098Z'
      props.filterState.params.jours = '0-1'
      const pickedDate = new Date('12/12/2034')
      const expected = {
        date: pickedDate.toISOString(),
        jours: null,
      }

      // when
      const wrapper = shallow(<FilterByDates {...props} />)
      wrapper.instance().onChangePickedDate(pickedDate)

      // then
      expect(props.filterActions.change).toHaveBeenCalledWith(expected)
      expect(wrapper.state(['pickedDate'])).toBe(pickedDate)
      props.filterActions.change.mockClear()
    })

    it('should call change filter action function without a date', () => {
      // given
      props.filterState.params.date = '2018-10-24T09:15:55.098Z'
      props.filterState.params.jours = '0-1'
      const expected = {
        date: null,
        jours: null,
      }

      // when
      const wrapper = shallow(<FilterByDates {...props} />)
      wrapper.instance().onChangePickedDate()

      // then
      expect(props.filterActions.change).toHaveBeenCalledWith(expected)
      expect(wrapper.state(['pickedDate'])).toBe(null)
      props.filterActions.change.mockClear()
    })
  })

  describe('onChangeDate()', () => {
    describe('when a day is checked for the first time', () => {
      it('should initialize date in query with a random range', () => {
        // given
        const day = '1-5'

        // when
        const wrapper = shallow(<FilterByDates {...props} />)
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBe(null)
        expect(props.filterActions.add).toHaveBeenCalled()
        props.filterActions.add.mockClear()
      })

      it('should change date to null when more than one days checked', () => {
        // given
        const day = '0-1'
        props.filterState.params.jours = day

        // when
        const wrapper = shallow(<FilterByDates {...props} />)
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBe(null)
        expect(props.filterActions.remove).toHaveBeenCalled()
        props.filterActions.remove.mockClear()
      })

      it('should check another day, already checked', () => {
        // given
        const day = '0-1'
        const callback = undefined
        props.filterState.params.jours = `${day},1-5`

        // when
        const wrapper = shallow(<FilterByDates {...props} />)
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBe(null)
        expect(props.filterActions.remove).toHaveBeenCalledWith(
          'jours',
          day,
          callback
        )
        props.filterActions.remove.mockClear()
      })

      it('shoud add another day not added yet to query with callback undefined ', () => {
        // given
        const day = '0-1'
        const callback = undefined
        props.filterState.params.jours = '1-5'

        // when
        const wrapper = shallow(<FilterByDates {...props} />)
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBe(null)
        expect(props.filterActions.add).toHaveBeenCalledWith(
          'jours',
          day,
          callback
        )
        props.filterActions.add.mockClear()
      })
    })
  })

  describe('componentDidUpdate()', () => {
    it('should set the picked date', () => {
      // when
      const wrapper = shallow(<FilterByDates {...props} />)
      wrapper.setProps({
        filterState: {
          params: {
            date: null,
          },
        },
        initialDateParams: true,
      })

      // then
      expect(wrapper.state(['pickedDate'])).toBe(null)
    })
  })

  describe('render()', () => {
    it('should have three checkboxes with right values and one DatePickerField', () => {
      // when
      const wrapper = shallow(<FilterByDates {...props} />)
      const checkboxes = wrapper.find('input[type="checkbox"]')
      const datePicker = wrapper.find(DatePickerField)

      // then
      expect(checkboxes).toHaveLength(3)
      DAYS_CHECKBOXES.forEach((checkbox, index) => {
        expect(checkboxes.at(index).props().value).toBe(checkbox.value)
      })
      expect(datePicker).toHaveLength(1)
    })
  })
})
