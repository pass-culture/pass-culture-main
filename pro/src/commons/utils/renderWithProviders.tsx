/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import { render } from '@testing-library/react'
import type { ReactNode } from 'react'
import { Provider } from 'react-redux'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { SWRConfig } from 'swr'

import type {
  FeatureResponseModel,
  SharedCurrentUserResponseModel,
} from '@/apiClient/v1'
import type { DeepPartial } from '@/commons/custom_types/utils'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'

import type { AnyObject } from './types'

interface RenderComponentFunctionParams<
  ComponentProps extends AnyObject | unknown = unknown,
  ContextValues extends AnyObject | unknown = unknown,
> {
  contextValues?: Partial<ContextValues>
  options?: RenderWithProvidersOptions
  path?: string
  props?: Partial<ComponentProps>
}
/**
 * Common Template-Type for integration tests render functions utilizing `renderWithProviders()`.
 */
export type RenderComponentFunction<
  ComponentProps extends AnyObject | unknown = unknown,
  ContextValues extends AnyObject | unknown = unknown,
  ExtraParams extends AnyObject | unknown = unknown,
> = (
  params: RenderComponentFunctionParams<ComponentProps, ContextValues> &
    ExtraParams
) => ReturnType<typeof renderWithProviders>

export type RenderWithProvidersOptions = {
  storeOverrides?: DeepPartial<RootState>
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
      id: index,
      isActive: true,
      name: feature,
    })
  )

  const storeOverrides: DeepPartial<RootState> = {
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

  const store = configureTestStore(storeOverrides as RootState)
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
    store,
  }
}
