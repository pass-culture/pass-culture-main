import { act, render } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import OfferLayoutContainer from 'components/pages/Offers/Offer/OfferLayoutContainer'
import { configureTestStore } from 'store/testUtils'
import routes from 'utils/routes_map'

export const renderOffer = async (initialEntries, store) => {
  const defaultStore = configureTestStore({
    data: {
      users: [
        { email: 'email@example.com', publicName: 'François', isAdmin: false },
      ],
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
            <OfferLayoutContainer />
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}
