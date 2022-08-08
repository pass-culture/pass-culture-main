import { act, render } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router-dom'

import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import routes from 'routes/routes_map'
import { configureTestStore } from 'store/testUtils'

export const renderOffer = async (initialEntries, store) => {
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

  await act(async () => {
    await render(
      <Provider store={store ? store : defaultStore}>
        <MemoryRouter initialEntries={[{ ...initialEntries }]}>
          <Route path={path}>
            <OfferLayout />
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}
