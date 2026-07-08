import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OnboardingLayout } from './OnboardingLayout'

const renderOnboardingLayout = (mainHeading?: string) => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/"
        element={
          <OnboardingLayout mainHeading={mainHeading}>Content</OnboardingLayout>
        }
      />
      <Route path="/accueil" element={<div>Accueil</div>} />
    </Routes>,
    { initialRouterEntries: ['/'] }
  )
}

describe('OnboardingLayout', () => {
  it('should always render a main landmark and a heading level 1', () => {
    renderOnboardingLayout('Main Heading')
    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  it('should display the page if the user can access onboarding', async () => {
    renderOnboardingLayout('Main Heading')
    await waitFor(() => {
      expect(screen.getByText('Content')).toBeInTheDocument()
    })
  })

  it('should not render title if not provided', () => {
    renderOnboardingLayout(undefined)
    expect(screen.queryByRole('heading', { level: 1 })).not.toBeInTheDocument()
  })
})
