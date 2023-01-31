import { render } from '@testing-library/react'
// c'est du bluff, l'import existe vraiment
// eslint-disable-next-line
import { LocationDescriptor } from 'history'
import React, { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

export const renderWithProviders = (
  component: ReactNode,
  overrides: {
    storeOverrides?: any
    initialRouterEntries?: LocationDescriptor<unknown>[]
  }
) => {
  const store = configureTestStore(overrides.storeOverrides)

  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={overrides.initialRouterEntries}>
        {component}
      </MemoryRouter>
    </Provider>
  )
}
