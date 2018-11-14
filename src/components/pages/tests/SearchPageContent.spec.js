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
        pagination: {},
        recommendations: [],
        search: {},
        typeSublabels: [],
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

  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state with functions', () => {
        // given
        const initialState = {}
        const store = mockStore(initialState)
        const props = {
          dispatch: jest.fn(),
          history: {},
          location: {},
          match: {},
          pagination: {},
          recommendations: [],
          search: {},
          typeSublabels: [],
        }

        // when
        shallow(
          <Provider store={store}>
            <SearchPageContent {...props} />
          </Provider>
        )
        // then
        // FAUX POSITIF car ne demande pas des props qui sont required pourtant... Le snapshot n'est pas bon non plus
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
