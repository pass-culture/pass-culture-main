import moment from 'moment'
import React from 'react'
import { shallow } from 'enzyme'

import FilterByDates from '../FilterByDates'

const filterActionsAddMock = jest.fn()
const filterActionsChangeMock = jest.fn()
const filterActionsRemoveMock = jest.fn()

const initialProps = {
  filterActions: {
    add: filterActionsAddMock,
    change: filterActionsChangeMock,
    remove: filterActionsRemoveMock,
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
  title: 'Fake title',
}

describe('src | components | pages | search | FilterByDates', () => {
  const filterActions = {
    add: filterActionsAddMock,
    change: filterActionsChangeMock,
    remove: filterActionsRemoveMock,
  }
  describe('snapshot', () => {
    // skipped because of minDate that make the tests allways false
    // Return a fixed timestamp when moment().format() is called
    jest.mock('moment', () => '2018-11-01T14:15:25.812')
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
    describe('isDaysChecked', () => {
      it('should ckeck boxes corresponding to days filtered', () => {
        const wrapper = shallow(<FilterByDates {...initialProps} />)
        const pickedDate = null
        const days = '0-1, 5-10000'
        const value = '0-1'
        const result = wrapper.instance().isDaysChecked(pickedDate, days, value)
        expect(result).toEqual(true)
      })
      it('should not ckeck box not corresponding to day filtered', () => {
        const wrapper = shallow(<FilterByDates {...initialProps} />)
        const pickedDate = null
        const days = '1-5'
        const value = '0-1'
        const result = wrapper.instance().isDaysChecked(pickedDate, days, value)
        expect(result).toEqual(false)
      })
      it('should not check date when a date is picked in calendar', () => {
        const wrapper = shallow(<FilterByDates {...initialProps} />)
        const pickedDate = moment()
        const days = '0-1'
        const value = '0-1'
        const result = wrapper.instance().isDaysChecked(pickedDate, days, value)
        expect(result).toEqual(false)
      })
    })
    describe('onPickedDateChange', () => {
      describe('when a date is picked', () => {
        it('should call change function with a date', () => {
          // given
          const props = {
            filterActions,
            filterState: {
              isNew: false,
              params: {
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
          const pickedDate = moment('12/12/2034')

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper.instance().onPickedDateChange(pickedDate)
          const expected = {
            date: pickedDate.toISOString(),
            jours: null,
          }

          // then
          expect(filterActionsChangeMock).toHaveBeenCalledWith(expected)
        })

        // pas de picked date
        it('should call change function without a date', () => {
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

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper.instance().onPickedDateChange()
          const expected = {
            date: null,
            jours: null,
          }

          // then
          expect(filterActionsChangeMock).toHaveBeenCalledWith(expected)
        })
      })
    })
    describe('OnChange', () => {
      describe('When a date is already selected with calendar', () => {
        it('it should set picked date from calendar to null', () => {
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

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper
            .find('input')
            .at(1)
            .simulate('change')

          // then
          expect(wrapper.state()).toEqual({ pickedDate: null })
        })
      })

      describe('When a day is checked for the first time', () => {
        it('Case 1 Should initialize date in query with today date', () => {
          // given
          const props = {
            filterActions,
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

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper
            .find('input')
            .at(1)
            .simulate('change')

          // then
          expect(filterActionsAddMock).toHaveBeenCalled()
          filterActionsAddMock.mockClear()
        })
        it('Case 2 Change date to null when more than one days checked', () => {
          // given
          const props = {
            filterActions,
            filterState: {
              isNew: false,
              query: {
                categories: null,
                date: null,
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

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper
            .find('input')
            .at(0)
            .simulate('change')

          // then
          expect(filterActionsRemoveMock).toHaveBeenCalled()
          filterActionsRemoveMock.mockClear()
        })
        it('Case 3 Check another day, already checked ', () => {
          // given
          const props = {
            filterActions,
            filterState: {
              isNew: false,
              query: {
                categories: null,
                date: null,
                distance: null,
                jours: '0-1,1-5',
                latitude: null,
                longitude: null,
                'mots-cles': null,
                orderBy: 'offer.id+desc',
              },
            },
            title: 'Fake title',
          }

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper
            .find('input')
            .at(0)
            .simulate('change')

          // then
          let callback
          expect(filterActionsRemoveMock).toHaveBeenCalledWith(
            'jours',
            '0-1',
            callback
          )
          filterActionsRemoveMock.mockClear()
        })

        it('Case 4 Add another day not added yet to query with callback undefined ', () => {
          // given
          const props = {
            filterActions,
            filterState: {
              isNew: false,
              query: {
                categories: null,
                date: null,
                distance: null,
                jours: '1-5',
                latitude: null,
                longitude: null,
                'mots-cles': null,
                orderBy: 'offer.id+desc',
              },
            },
            title: 'Fake title',
          }

          // when
          const wrapper = shallow(<FilterByDates {...props} />)
          wrapper
            .find('input')
            .at(0)
            .simulate('change')

          // then
          let callback
          expect(filterActionsAddMock).toHaveBeenCalledWith(
            'jours',
            '0-1',
            callback
          )
          filterActionsAddMock.mockClear()
        })
      })
    })
  })
})
