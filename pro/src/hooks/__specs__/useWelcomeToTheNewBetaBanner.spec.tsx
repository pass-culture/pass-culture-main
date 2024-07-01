import { screen } from '@testing-library/react'

import { useWelcomeToTheNewBetaBanner } from 'hooks/useWelcomeToTheNewBetaBanner'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

const TestComponent = () => {
  const showModalForNonBetaTest = useWelcomeToTheNewBetaBanner()

  return <div>{showModalForNonBetaTest ? 'Modal Open' : 'Modal Closed'}</div>
}

const defaultOptions: RenderWithProvidersOptions = {
  user: sharedCurrentUserFactory(),
  features: [],
}

const renderWelcomeToTheNewBetaBanner = (
  options: RenderWithProvidersOptions = defaultOptions
) => {
  return renderWithProviders(<TestComponent />, { ...options })
}

describe('useShowModalForNonBetaTest', () => {
  it('should return false if user is not connected', () => {
    const options = { user: null }
    renderWelcomeToTheNewBetaBanner(options)
    expect(screen.getByText('Modal Closed')).toBeInTheDocument()
  })

  it('should return false if user connected but as no new nav date', () => {
    const options = {
      user: sharedCurrentUserFactory({
        navState: {
          newNavDate: undefined,
        },
      }),
    }
    renderWelcomeToTheNewBetaBanner(options)
    expect(screen.getByText('Modal Closed')).toBeInTheDocument()
  })

  it('should return false if user has new nav date is before 09/07/2024', () => {
    const options = {
      user: sharedCurrentUserFactory({
        navState: {
          newNavDate: '2024-07-01 00:00:00.000000',
        },
      }),
    }
    renderWelcomeToTheNewBetaBanner(options)
    expect(screen.getByText('Modal Closed')).toBeInTheDocument()
  })

  it('should return false if user has registered after 09/07/2024', () => {
    const options = {
      user: sharedCurrentUserFactory({
        dateCreated: '2024-07-30 00:00:00.000000',
      }),
    }
    renderWelcomeToTheNewBetaBanner(options)
    expect(screen.getByText('Modal Closed')).toBeInTheDocument()
  })

  it('should return true if new nav date is after 09/07/2024 AND registered before 09/07/2024', () => {
    const options = {
      user: sharedCurrentUserFactory({
        dateCreated: '2024-07-01 00:00:00.000000',
        navState: {
          newNavDate: '2024-07-30 00:00:00.000000',
        },
      }),
    }
    renderWelcomeToTheNewBetaBanner(options)
    expect(screen.getByText('Modal Open')).toBeInTheDocument()
  })
})
