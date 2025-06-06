/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { render } from '@testing-library/react'
import { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { SWRConfig } from 'swr'

import {
  FeatureResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import { RootState } from 'commons/store/rootReducer'
import { configureTestStore } from 'commons/store/testUtils'

export type RenderWithProvidersOptions = {
  storeOverrides?: Partial<RootState>
  initialRouterEntries?: string[]
  features?: string[]
  user?: SharedCurrentUserResponseModel | null
}

const createRouterFromOverrides = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions,
  initialPath: string = '*'
) =>
  createMemoryRouter([{ path: initialPath, element: component }], {
    initialEntries: overrides?.initialRouterEntries,
    future: {
      //v7_relativeSplatPath: true,
      //v7_startTransition: true,
      //v7_fetcherPersist: true,
      //v7_normalizeFormMethod: true,
      //v7_partialHydration: true,
      //v7_skipActionErrorRevalidation: true,
    },
  })

export const renderWithProviders = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions,
  initialPath?: string
) => {
  // Added here to mock the sidebar collapse for all the tests
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: () => ({
      matches: false,
      addListener: vi.fn(),
      removeListener: vi.fn(),
    }),
  })

  const featuresList = (overrides?.features ?? []).map(
    (feature, index): FeatureResponseModel => ({
      id: String(index),
      isActive: true,
      nameKey: feature,
      name: feature,
      description: '',
    })
  )

  const storeOverrides: Partial<RootState> = {
    ...overrides?.storeOverrides,
    features: {
      list: featuresList,
      lastLoaded: overrides?.storeOverrides?.features?.lastLoaded,
    },
    user: overrides?.user
      ? {
          currentUser: overrides.user,
          ...overrides.storeOverrides?.user,
        }
      : overrides?.storeOverrides?.user,
    offerer: overrides?.storeOverrides?.offerer,
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
