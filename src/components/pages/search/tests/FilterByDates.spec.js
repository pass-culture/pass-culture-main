import moment from 'moment'
import React from 'react'
import { shallow } from 'enzyme'

import FilterByDates from '../FilterByDates'
import { TODAY_DATE } from '../utils'

const filterActionsAdd = jest.fn()
const filterActionsChange = jest.fn()
const filterActionsRemove = jest.fn()
const filterActionsReplace = jest.fn()

const initialProps = {
  filterActions: {
    add: filterActionsAdd,
    change: filterActionsChange,
    remove: filterActionsRemove,
    replace: filterActionsReplace,
  },
  filterState: {
    isNew: false,
    query: {
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
  title: 'Fake title',
}

describe('src | components | pages | search | FilterByDates', () => {
  const filterActions = {
    add: filterActionsAdd,
    change: filterActionsChange,
    remove: filterActionsRemove,
    replace: filterActionsReplace,
  }
  describe.skip('snapshot', () => {
    // skipped because of minDate that make the tests allways false
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<FilterByDates {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions ', () => {
    // WE ADD THE DATE AT THE FIRST DAYS SEGMENTS CLICKED
    // WE REMOVE THE DATE AT THE LAST DAYS SEGMENTS CLICKED
    describe('isDateChecked', () => {
      it('should ckeck boxes corresponding to days filtered', () => {
        const wrapper = shallow(<FilterByDates {...initialProps} />)
        const pickedDate = null
        const days = '0-1, 5-10000'
        const value = '0-1'
        const result = wrapper.instance().isDateChecked(pickedDate, days, value)
        expect(result).toEqual(true)
      })
      it('should not ckeck box not corresponding to day filtered', () => {
        const wrapper = shallow(<FilterByDates {...initialProps} />)
        const pickedDate = null
        const days = '1-5'
        const value = '0-1'
        const result = wrapper.instance().isDateChecked(pickedDate, days, value)
        expect(result).toEqual(false)
      })
      it('should not check date when a date is picked in calendar', () => {
        const wrapper = shallow(<FilterByDates {...initialProps} />)
        const pickedDate = moment()
        const days = '0-1'
        const value = '0-1'
        const result = wrapper.instance().isDateChecked(pickedDate, days, value)
        expect(result).toEqual(false)
      })
    })
    describe('onPickedDateChange', () => {
      describe('when a date is picked', () => {
        it('should call change function with good parameters', () => {
          // given
          const props = {
            filterActions,
            filterState: {
              isNew: false,
              query: {
                categories: null,
                date: '2018-10-24T09:15:55.098Z',
                distance: null,
                jours: '0-1',
                latitude: null,
                longitude: null,
                'mots-cles': null,
                orderBy: 'offer.id+desc',
              },
            },
            title: 'Fake title',
          }
          const pickedDate = TODAY_DATE

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper.instance().onPickedDateChange(pickedDate)
          const expected = {
            date: pickedDate.toISOString(),
            jours: null,
          }

          // then
          expect(filterActionsChange).toHaveBeenCalledWith(expected)
        })
        it('should uncheck days checkboxes ', () => {
          // TODO
        })
      })
    })
  })
})
