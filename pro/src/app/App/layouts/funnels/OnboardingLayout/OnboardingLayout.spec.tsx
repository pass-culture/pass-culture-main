import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OnboardingLayout } from './OnboardingLayout'

const renderOnboardingLayout = () => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/"
        element={
          <OnboardingLayout mainHeading="Title">Content</OnboardingLayout>
        }
      />
      <Route path="/accueil" element={<div>Accueil</div>} />
    </Routes>,
    { initialRouterEntries: ['/'] }
  )
}

describe('OnboardingLayout', () => {
  it('should always render a main landmark and a heading level 1', () => {
    renderOnboardingLayout()
    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  it('should display the page if the user can access onboarding', async () => {
    renderOnboardingLayout()
    await waitFor(() => {
      expect(screen.getByText('Content')).toBeInTheDocument()
    })
  })
})
