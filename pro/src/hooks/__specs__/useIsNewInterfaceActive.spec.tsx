import { screen } from '@testing-library/react'
import React from 'react'

import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

const TestComponent = () => {
  const isSideNavActive = useIsNewInterfaceActive()

  return <div>{isSideNavActive ? 'Active' : 'Inactive'}</div>
}

const defaultOptions: RenderWithProvidersOptions = {
  storeOverrides: {
    user: { currentUser: { isAdmin: false } },
  },
  features: [],
}

const renderUseIsNewInterfaceActive = (
  options: RenderWithProvidersOptions = defaultOptions
) => {
  return renderWithProviders(<TestComponent />, { ...options })
}

describe('useIsNewInterfaceActive', () => {
  it('should return true if the feature is active and user has new nav date', () => {
    const options = {
      features: ['WIP_ENABLE_PRO_SIDE_NAV'],
      storeOverrides: {
        user: {
          currentUser: {
            isAdmin: false,
            navState: {
              newNavDate: '2021-01-01',
            },
          },
        },
      },
    }
    renderUseIsNewInterfaceActive(options)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('should return false if user is not connected', () => {
    const options = {
      features: ['WIP_ENABLE_PRO_SIDE_NAV'],
      storeOverrides: {
        user: {
          currentUser: null,
        },
      },
    }
    renderUseIsNewInterfaceActive(options)
    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })

  it('should return false if the feature is inactive', () => {
    const options = {
      features: [],
      storeOverrides: {
        user: {
          currentUser: {
            isAdmin: false,
            navState: {
              newNavDate: '2021-01-01',
            },
          },
        },
      },
    }
    renderUseIsNewInterfaceActive(options)
    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })

  it('should return false if user connected but as no new nav date', () => {
    const options = {
      features: ['WIP_ENABLE_PRO_SIDE_NAV'],
      storeOverrides: {
        user: {
          currentUser: {
            isAdmin: false,
            navState: {
              newNavDate: null,
            },
          },
        },
      },
    }
    renderUseIsNewInterfaceActive(options)
    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })
})
