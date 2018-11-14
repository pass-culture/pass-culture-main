import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import SearchPageContent from '../SearchPageContent'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | SearchPageContentContent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const props = {
        dispatch: jest.fn(),
        history: {},
        location: {},
        match: {},
        pagination: {
          windowQuery: {
            categories: null,
            date: null,
            distance: null,
            jours: null,
            latitude: null,
            longitude: null,
            'mots-cles': 'Fake',
            orderBy: 'offer.id+desc',
          },
        },
        recommendations: [],
        search: {},
        typeSublabels: [],
        typeSublabelsAndDescription: [],
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <SearchPageContent {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  //
  // describe.skip('render', () => {
  //   // given
  //   const initialState = REDUX_STATE
  //   const store = mockStore(initialState)
  //   const wrapper = shallow(<SearchPageContent store={store} />)
  //
  // })

  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // given
        const props = {
          dispatch: jest.fn(),
          history: {},
          location: {
            hash: '',
            key: 'lxn6vp',
            pathname: '/recherche',
            search: '?orderBy=offer.id+desc',
            state: undefined,
          },
          match: {
            params: {
              categorie: undefined,
              view: undefined,
            },
          },
          pagination: {
            windowQuery: {
              categories: null,
              date: null,
              distance: null,
              jours: null,
              latitude: null,
              longitude: null,
              'mots-cles': 'Fake',
              orderBy: 'offer.id+desc',
            },
          },
          recommendations: [],
          search: {},
          typeSublabels: [],
          typeSublabelsAndDescription: [],
        }

        // when
        const wrapper = shallow(<SearchPageContent {...props} />)
        const expected = {
          keywordsKey: 0,
          keywordsValue: 'Fake',
          withFilter: false,
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })
    describe('handleDataRequest', () => {
      it('should', () => {})
    })
    describe('loadMoreHandler', () => {
      it('should', () => {})
    })
    describe('onBackToSearchHome', () => {
      it('should', () => {})
    })
    describe('onSubmit', () => {
      it('should', () => {})
    })
    describe('onClickOpenCloseFilterDiv', () => {
      it('should', () => {})
    })
    describe('onKeywordsChange', () => {
      it('should', () => {})
    })
    describe('onKeywordsEraseClick', () => {
      it('should', () => {})
    })
  })
})

// Titre de la page selon s'il y a des recommendations ou pas.
