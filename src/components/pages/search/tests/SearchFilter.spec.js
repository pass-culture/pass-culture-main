import React from 'react'
import { shallow } from 'enzyme'

import SearchFilter from '../SearchFilter'
import { INITIAL_FILTER_PARAMS } from '../utils'

const paginationChangeMock = jest.fn()

describe('src | components | pages | search | SearchFilter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        isVisible: true,
        pagination: {
          windowQuery: {
            categories: null,
            date: '2018-09-28T12:52:52.341Z',
            distance: '50',
            jours: '0-1',
            latitude: '48.8637546',
            longitude: '2.337428',
            [`mots-cles`]: 'fake',
            orderBy: 'offer.id+desc',
          },
        },
      }

      // when
      const wrapper = shallow(<SearchFilter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('functions', () => {
    describe('constructor', () => {
      it.skip('should initilize state with functions', () => {
        // given
        const props = {
          isVisible: false,
          pagination: {
            windowQuery: {},
          },
        }

        // when
        const wrapper = shallow(<SearchFilter {...props} />)
        wrapper.instance().handleQueryAdd = jest.fn()
        wrapper.instance().handleQueryChange = jest.fn()
        wrapper.instance().handleQueryRemove = jest.fn()

        // then
        expect(wrapper.state().add).toEqual('mocked function handleQueryAdd ')
      })
    })

    describe('onComponentDidUpdate', () => {
      it('should update state if query has changed', () => {
        // given
        const props = {
          isVisible: false,
          pagination: {
            windowQuery: {
              categories: 'Jouer',
              date: null,
              distance: null,
              jours: '1-5',
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'fake',
              orderBy: 'offer.id+desc',
            },
          },
        }

        const prevProps = {
          isVisible: false,
          pagination: {
            windowQuery: {
              categories: 'Jouer',
              date: null,
              distance: null,
              jours: '1-5',
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'fake',
              orderBy: 'offer.id+desc',
            },
          },
        }

        // when
        const wrapper = shallow(<SearchFilter {...props} />)
        wrapper.instance().componentDidUpdate(prevProps)

        // the
        const updatedQuery = wrapper.state('query')
        const isNewKey = wrapper.state('isNew')
        const expected = {
          categories: 'Jouer',
          date: null,
          distance: null,
          jours: '1-5',
          latitude: null,
          longitude: null,
          'mots-cles': 'fake',
          orderBy: 'offer.id+desc',
        }
        expect(updatedQuery).toEqual(expected)
        expect(isNewKey).toEqual(false)
      })
    })

    describe('onResetClick', () => {
      it('should call hoc pagination change method with the good parameters', () => {
        // given
        const props = {
          isVisible: true,
          pagination: {
            change: paginationChangeMock,
            windowQuery: {
              categories: null,
              date: '2018-09-28T12:52:52.341Z',
              distance: '50',
              jours: '0-1',
              latitude: '48.8637546',
              longitude: '2.337428',
              [`mots-cles`]: 'fake',
              orderBy: 'offer.id+desc',
            },
          },
        }

        // when
        const wrapper = shallow(<SearchFilter {...props} />)
        wrapper.instance().onResetClick()
        const updatedFormState = wrapper.state('isNew')

        expect(updatedFormState).toEqual('date')

        expect(paginationChangeMock).toHaveBeenCalledWith(
          INITIAL_FILTER_PARAMS,
          { pathname: '/recherche/resultats' }
        )
      })
    })

    describe('onFilterClick', () => {
      it('should call hoc pagination change method with the good parameters', () => {
        // given
        const props = {
          isVisible: true,
          pagination: {
            change: paginationChangeMock,
            windowQuery: {
              categories: null,
              date: null,
              distance: '50',
              jours: null,
              latitude: '48.8637546',
              longitude: '2.337428',
              [`mots-cles`]: 'fake',
              orderBy: 'offer.id+desc',
            },
          },
        }

        // when
        const wrapper = shallow(<SearchFilter {...props} />)
        wrapper.instance().onFilterClick()
        const currentQuery = wrapper.state('query')
        const updatedFormState = wrapper.state('isNew')

        // THEN
        expect(paginationChangeMock).toHaveBeenCalledWith(currentQuery, {
          isClearingData: false,
          pathname: '/recherche/resultats',
        })

        expect(updatedFormState).toEqual(false)
      })
    })

    // handleQueryChange
    // handleQueryAdd
    // handleQueryRemove
  })
})
