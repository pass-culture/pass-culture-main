import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import * as useHasAccessToDidacticOnboarding from '@/commons/hooks/useHasAccessToDidacticOnboarding'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { OnboardingLayout } from '@/pages/Onboarding/components/OnboardingLayout/OnboardingLayout'

const renderOnboardingLayout = () => {
  return renderWithProviders(
    <Routes>
      <Route path="/" element={<OnboardingLayout>Content</OnboardingLayout>} />
      <Route path="/accueil" element={<div>Accueil</div>} />
    </Routes>,
    { initialRouterEntries: ['/'] }
  )
}

describe('<OnboardingOfferIndividual />', () => {
  it("Should redirect to homepage if the user can't access the onboarding", async () => {
    vi.spyOn(
      useHasAccessToDidacticOnboarding,
      'useHasAccessToDidacticOnboarding'
    ).mockReturnValue(false)

    renderOnboardingLayout()
    await waitFor(() => {
      expect(screen.getByText('Accueil')).toBeInTheDocument()
    })
  })

  it('Should display the page if the user can access onboarding', async () => {
    vi.spyOn(
      useHasAccessToDidacticOnboarding,
      'useHasAccessToDidacticOnboarding'
    ).mockReturnValue(true)

    renderOnboardingLayout()
    await waitFor(() => {
      expect(screen.getByText('Content')).toBeInTheDocument()
    })
  })
})
