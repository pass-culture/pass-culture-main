/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { render } from '@testing-library/react'
import React, { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

export type RenderWithProvidersOptions = {
  // TODO change any to Partial<RootState> and use factories for each slice
  storeOverrides?: any
  initialRouterEntries?: string[]
  features?: string[]
}

const createRouterFromOverrides = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions,
  initialPath: string = '*'
) =>
  createMemoryRouter([{ path: initialPath, element: component }], {
    initialEntries: overrides?.initialRouterEntries,
  })

export const renderWithProviders = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions,
  initialPath?: string
) => {
  const featuresList = (overrides?.features ?? []).map((feature) => ({
    isActive: true,
    nameKey: feature,
  }))

  const storeOverrides = {
    ...overrides?.storeOverrides,
    features: {
      list: featuresList,
      lastLoaded: overrides?.storeOverrides?.features?.lastLoaded,
    },
  }
  const store = configureTestStore(storeOverrides)
  const router = createRouterFromOverrides(component, overrides, initialPath)

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
