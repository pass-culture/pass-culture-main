/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { render } from '@testing-library/react'
import React, { ReactNode } from 'react'
import { I18nextProvider } from 'react-i18next'
import { Provider } from 'react-redux'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { SWRConfig } from 'swr'

import {
  FeatureResponseModel,
  SharedCurrentUserResponseModel,
} from 'apiClient/v1'
import { RootState } from 'store/rootReducer'
import { configureTestStore } from 'store/testUtils'

import i18n from './i18nForTests'

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
  })

export const renderWithi18nProvider = (children: ReactNode) => {
  render(<I18nextProvider i18n={i18n}>{children}</I18nextProvider>)
}

export const renderWithProviders = (
  component: ReactNode,
  overrides?: RenderWithProvidersOptions,
  initialPath?: string
) => {
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
          selectedOffererId: null,
          currentUser: overrides.user,
          ...overrides.storeOverrides?.user,
        }
      : overrides?.storeOverrides?.user,
  }

  const store = configureTestStore(storeOverrides)
  const router = createRouterFromOverrides(component, overrides, initialPath)

  const { rerender, ...otherRenderResult } = render(
    <Provider store={store}>
      <I18nextProvider i18n={i18n}>
        <SWRConfig value={{ provider: () => new Map() }}>
          <RouterProvider router={router} />
        </SWRConfig>
      </I18nextProvider>
    </Provider>
  )

  return {
    ...otherRenderResult,
    rerender: (newChildren: ReactNode) => {
      const router = createRouterFromOverrides(newChildren, overrides)

      return rerender(
        <Provider store={store}>
          <I18nextProvider i18n={i18n}>
            <SWRConfig value={{ provider: () => new Map() }}>
              <RouterProvider router={router} />
            </SWRConfig>
          </I18nextProvider>
        </Provider>
      )
    },
  }
}
