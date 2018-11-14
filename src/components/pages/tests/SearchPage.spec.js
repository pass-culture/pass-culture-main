import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import SearchPage from '../SearchPage'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | SearchPage', () => {
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
          <SearchPage {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe.skip('mapStateToProps', () => {
    it('should update props values ', () => {
      // given
      const initialState = {
        data: {
          types: [
            {
              description:
                'Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
              id: 0,
              label: 'Cinéma (Projections, Séances, Évènements)',
              offlineOnly: true,
              onlineOnly: false,
              sublabel: 'Regarder',
              type: 'Event',
              value: 'EventType.CINEMA',
            },
          ],
        },
      }
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
          <SearchPage {...props} />
        </Provider>
      )

      // then
      expect(wrapper.props().typeSublabels).toEqual()
    })
  })
})
