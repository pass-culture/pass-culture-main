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
  it('should return true if user has new nav date', () => {
    const options = {
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
      storeOverrides: {
        user: {
          currentUser: null,
        },
      },
    }
    renderUseIsNewInterfaceActive(options)
    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })

  it('should return false if user connected but as no new nav date', () => {
    const options = {
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

  it('should return false if user connected but as new nav date in future', () => {
    const options = {
      storeOverrides: {
        user: {
          currentUser: {
            isAdmin: false,
            navState: {
              newNavDate: '2999-01-01',
            },
          },
        },
      },
    }
    renderUseIsNewInterfaceActive(options)
    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })
})
