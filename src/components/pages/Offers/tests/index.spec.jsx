import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import { Provider } from 'react-redux'
import React from 'react'
import { connect } from 'react-redux'
import { Route, Router } from 'react-router'
import { compose } from 'redux'
import configureStore from 'redux-mock-store'

import withFrenchQueryRouter from '../../../../components/hocs/withFrenchQueryRouter'
import Offers from '../Offers'
import { mapStateToProps } from '../OffersContainer'

const Offers = compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Offers)

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
        user: {
          publicName: 'super nom'
        }
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
        .find('Offers')
        .find('.delete')
        .props()
        .onClick()

      // then
      const queryParams = wrapper
        .find('Offers')
        .props()
        .query.parse()
      expect(queryParams).toEqual({})
    })
  })
})
