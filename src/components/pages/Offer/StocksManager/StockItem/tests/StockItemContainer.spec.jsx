import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import configureStore from 'redux-mock-store'

import StockItemContainer from '../StockItemContainer'

describe('mount', () => {
  it('should reset the form when click on cancel button', () => {
    // given
    const history = createBrowserHistory()
    history.push(`/offres/AE?gestion&stockAE=modification`)
    const middlewares = []
    const mockStore = configureStore(middlewares)
    const stock = { offerId: 'AE', id: 'AE' }
    const store = mockStore({
      data: {
        offers: [{ id: 'AE', venueId: 'AE' }],
        offerers: [{ id: 'AE' }],
        products: [{ id: 'AE' }],
        stocks: [stock],
        venues: [{ id: 'AE', managingOffererId: 'AE' }],
      },
    })

    const props = {
      isEvent: true,
      stock,
    }

    const wrapper = mount(
      <Provider store={store}>
        <Router history={history}>
          <Switch>
            <Route path="/offres/:offerId">
              <StockItemContainer {...props} />
            </Route>
          </Switch>
        </Router>
      </Provider>
    )

    // when
    wrapper
      .find("input[name='beginningTime']")
      .simulate('change', { target: { value: '12:13' } })

    expect(wrapper.find("input[name='beginningTime']").props().value).toEqual(
      '12:13'
    )

    // when
    const cancelButton = wrapper.find('button[type="reset"]')
    cancelButton.simulate('click')

    // then
    expect(wrapper.find("input[name='beginningTime']").props().value).toEqual(
      ''
    )
  })
})
