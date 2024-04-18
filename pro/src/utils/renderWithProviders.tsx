/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { render } from '@testing-library/react'
import React, { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { SWRConfig } from 'swr'

import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { RootState } from 'store/rootReducer'
import { configureTestStore } from 'store/testUtils'

export type RenderWithProvidersOptions = {
  // TODO change any to Partial<RootState> and use factories for each slice
  storeOverrides?: any
  initialRouterEntries?: string[]
  features?: string[]
  user?: Partial<SharedCurrentUserResponseModel>
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

  const storeOverrides: Partial<RootState> = {
    ...overrides?.storeOverrides,
    features: {
      list: featuresList,
      lastLoaded: overrides?.storeOverrides?.features?.lastLoaded,
    },
    user: overrides?.user
      ? {
          ...overrides.storeOverrides?.user,
          selectedOffererId: true,
          currentUser: overrides.user,
        }
      : overrides?.storeOverrides?.user,
  }

  const store = configureTestStore(storeOverrides)
  const router = createRouterFromOverrides(component, overrides, initialPath)

  const { rerender, ...otherRenderResult } = render(
    <Provider store={store}>
      <SWRConfig value={{ provider: () => new Map() }}>
        <RouterProvider router={router} />
      </SWRConfig>
    </Provider>
  )

  return {
    ...otherRenderResult,
    rerender: (newChildren: ReactNode) => {
      const router = createRouterFromOverrides(newChildren, overrides)

      return rerender(
        <Provider store={store}>
          <SWRConfig value={{ provider: () => new Map() }}>
            <RouterProvider router={router} />
          </SWRConfig>
        </Provider>
      )
    },
  }
}
