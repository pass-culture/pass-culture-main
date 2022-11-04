import { render } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router-dom'

import routes from 'app/AppRouter/routes_map'
import OfferLayout from 'pages/Offers/Offer/OfferLayout'
import { configureTestStore } from 'store/testUtils'

export const renderOffer = (initialEntries, store) => {
  const defaultStore = configureTestStore({
    user: {
      currentUser: {
        email: 'email@example.com',
        publicName: 'François',
        isAdmin: false,
      },
    },
  })
  let path = ''

  Object.keys(routes).forEach(key => {
    if (routes[key].title === 'Offre') {
      path = routes[key].path
    }
  })

  render(
    <Provider store={store ? store : defaultStore}>
      <MemoryRouter initialEntries={[{ ...initialEntries }]}>
        <Route path={path}>
          <OfferLayout />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}
