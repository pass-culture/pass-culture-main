import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import { Provider } from 'react-redux'
import React from 'react'
import { connect } from 'react-redux'
import { Route, Router } from 'react-router'
import { compose } from 'redux'
import configureStore from 'redux-mock-store'

import { withFrenchQueryRouter } from 'components/hocs'
import RawOffers from '../RawOffers'
import { mapStateToProps } from '../index'

fetch.mockResponse(JSON.stringify([]), { status: 200 })

const Offers = compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(RawOffers)

describe('src | components | pages | Offers', () => {
  describe('click on ui filters', () => {
    it('should redirect to /offres when click on venue flag', () => {
      // given
      const initialProps = {
        currentUser: { id: 'AE', currentUserUUID: 'baba' },
        dispatch: jest.fn(),
        venue: {},
      }
      const store = configureStore()({
        data: {
          offers: [],
          offerers: [],
          venues: [{ id: 'AE' }],
          types: [],
          users: [{ id: 'AE', currentUserUUID: 'baba' }],
        },
        modal: {},
        tracker: {},
      })
      const history = createBrowserHistory()
      history.push('/offres?lieu=AE')
      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Route path="/offres">
              <Offers {...initialProps} />
            </Route>
          </Router>
        </Provider>
      )

      // when
      wrapper
        .find('RawOffers')
        .find('.delete')
        .props()
        .onClick()

      // given
      const queryParams = wrapper
        .find('RawOffers')
        .props()
        .query.parse()
      expect(queryParams).toEqual({})
    })
  })
})
