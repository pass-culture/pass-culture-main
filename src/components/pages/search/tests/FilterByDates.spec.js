import { shallow } from 'enzyme'
import React from 'react'

import { DatePickerField } from '../../../forms/inputs'
import FilterByDates from '../FilterByDates'
import { DAYS_CHECKBOXES } from '../utils'

describe('src | components | pages | search | FilterByDates', () => {
  let props

  beforeEach(() => {
    props = {
      filterActions: {
        add: jest.fn(),
        change: jest.fn(),
        remove: jest.fn(),
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
    jest.spyOn(global, 'Date').mockImplementation(() => snapshotDate)

    // when
    const wrapper = shallow(<FilterByDates {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleOnChangePickedDate()', () => {
    it('should change the input date with the new date', () => {
      // given
      const pickedDate = new Date('12/12/2034')
      const wrapper = shallow(<FilterByDates {...props} />)

      // when
      wrapper.instance().handleOnChangePickedDate(pickedDate)

      // then
      expect(props.filterActions.change).toHaveBeenCalledWith({
        date: pickedDate.toISOString(),
        jours: null,
      })
      expect(wrapper.state(['pickedDate'])).toBe(pickedDate)
    })

    it('should remove the input date ', () => {
      // given
      const wrapper = shallow(<FilterByDates {...props} />)

      // when
      wrapper.instance().handleOnChangePickedDate()

      // then
      expect(props.filterActions.change).toHaveBeenCalledWith({
        date: null,
        jours: null,
      })
      expect(wrapper.state(['pickedDate'])).toBeNull()
    })
  })

  describe('onChangeDate()', () => {
    describe('when a day is checked for the first time', () => {
      it('should initialize date in query with a random range', () => {
        // given
        const day = '1-5'
        const wrapper = shallow(<FilterByDates {...props} />)

        // when
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBeNull()
        expect(props.filterActions.add).toHaveBeenCalled()
      })

      it('should change date to null when more than one days checked', () => {
        // given
        const day = '0-1'
        props.filterState.params.jours = day
        const wrapper = shallow(<FilterByDates {...props} />)

        // when
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBeNull()
        expect(props.filterActions.remove).toHaveBeenCalled()
      })

      it('should check another day, already checked', () => {
        // given
        const day = '0-1'
        const callback = undefined
        props.filterState.params.jours = `${day},1-5`
        const wrapper = shallow(<FilterByDates {...props} />)

        // when
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBeNull()
        expect(props.filterActions.remove).toHaveBeenCalledWith('jours', day, callback)
      })

      it('shoud add another day not added yet to query with callback undefined ', () => {
        // given
        const day = '0-1'
        const callback = undefined
        props.filterState.params.jours = '1-5'
        const wrapper = shallow(<FilterByDates {...props} />)

        // when
        wrapper.instance().onChangeDate(day)()

        // then
        expect(wrapper.state(['pickedDate'])).toBeNull()
        expect(props.filterActions.add).toHaveBeenCalledWith('jours', day, callback)
      })
    })
  })

  describe('componentDidUpdate()', () => {
    it('should set the input date', () => {
      // given
      const wrapper = shallow(<FilterByDates {...props} />)

      // when
      wrapper.setProps({
        filterState: {
          params: {
            date: null,
          },
        },
        initialDateParams: true,
      })

      // then
      expect(wrapper.state(['pickedDate'])).toBeNull()
    })
  })

  describe('render()', () => {
    it('should have three checkboxes with right values and one DatePickerField by default', () => {
      // given
      const wrapper = shallow(<FilterByDates {...props} />)

      // when
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
