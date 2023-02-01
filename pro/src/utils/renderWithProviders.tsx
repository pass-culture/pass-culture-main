import { render } from '@testing-library/react'
import type { LocationDescriptor } from 'history'
import React, { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import { CompatRouter } from 'react-router-dom-v5-compat'

import { configureTestStore } from 'store/testUtils'

const identity = ({ children }: { children: ReactNode }) => children

export const renderWithProviders = (
  component: ReactNode,
  overrides?: {
    storeOverrides?: any
    initialRouterEntries?: LocationDescriptor<unknown>[]
    // Some tests cannot use the Compatibility Router because they do some expects
    // on history.push or mock useHistory in some way. Those tests should be refactored
    // to not assert on history.push or assert on useNavigate
    // as react-router-v6 drops the history dependency
    // This setting is here as a temporary solution to allow us to migrate
    // progressively to react-router-v6
    TOREFACTOR_doNotUseV6CompatRouter?: boolean
  }
) => {
  const store = configureTestStore(overrides?.storeOverrides)
  const ReactRouterV6Adapter = overrides?.TOREFACTOR_doNotUseV6CompatRouter
    ? identity
    : CompatRouter

  const { rerender, ...otherRenderResult } = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={overrides?.initialRouterEntries}>
        {/* Temporary router for react-router v6 migration */}
        {/* https://www.npmjs.com/package/react-router-dom-v5-compat */}
        {/* @ts-expect-error temporary solution */}
        <ReactRouterV6Adapter>{component}</ReactRouterV6Adapter>
      </MemoryRouter>
    </Provider>
  )

  return {
    ...otherRenderResult,
    rerender: (newChildren: ReactNode) =>
      rerender(
        <Provider store={store}>
          <MemoryRouter initialEntries={overrides?.initialRouterEntries}>
            {/* @ts-expect-error temporary solution */}
            <ReactRouterV6Adapter>{newChildren}</ReactRouterV6Adapter>
          </MemoryRouter>
        </Provider>
      ),
  }
}
