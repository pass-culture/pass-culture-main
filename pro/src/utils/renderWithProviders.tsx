/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { render } from '@testing-library/react'
import React, { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { createMemoryRouter, RouterProvider } from 'react-router-dom-v5-compat'

import { configureTestStore } from 'store/testUtils'

interface RenderWithProvidersOptions {
  storeOverrides?: any
  initialRouterEntries?: string[]
}

const createRouterFromOverrides = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions
) =>
  createMemoryRouter([{ path: '*', element: component }], {
    initialEntries: overrides?.initialRouterEntries,
  })

export const renderWithProviders = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions
) => {
  const store = configureTestStore(overrides?.storeOverrides)
  const router = createRouterFromOverrides(component, overrides)

  const { rerender, ...otherRenderResult } = render(
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  )

  return {
    ...otherRenderResult,
    rerender: (newChildren: ReactNode) => {
      const router = createRouterFromOverrides(newChildren, overrides)

      return rerender(
        <Provider store={store}>
          <RouterProvider router={router} />
        </Provider>
      )
    },
  }
}
