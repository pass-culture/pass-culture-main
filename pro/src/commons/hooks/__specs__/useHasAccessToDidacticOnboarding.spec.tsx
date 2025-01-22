import { screen } from '@testing-library/react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

const TestComponent = () => {
  return <div>{useHasAccessToDidacticOnboarding() ? 'OUI' : 'NON'}</div>
}

const renderuseHasAccessToDidacticOnboarding = (features: string[] = []) => {
  return renderWithProviders(<TestComponent />, { features })
}

describe('useHasAccessToDidacticOnboarding', () => {
  describe('With AB test disabled', () => {
    it('should return true if WIP_ENABLE_PRO_DIDACTIC_ONBOARDING is enabled', () => {
      renderuseHasAccessToDidacticOnboarding([
        'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
      ])

      expect(screen.getByText('OUI')).toBeInTheDocument()
    })

    it('should return false if WIP_ENABLE_PRO_DIDACTIC_ONBOARDING is disabled', () => {
      renderuseHasAccessToDidacticOnboarding()
      expect(screen.getByText('NON')).toBeInTheDocument()
    })
  })

  describe('With AB test enabled', () => {
    it('should return false if WIP_ENABLE_PRO_DIDACTIC_ONBOARDING is disabled', () => {
      renderuseHasAccessToDidacticOnboarding([
        'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST',
      ])

      expect(screen.getByText('NON')).toBeInTheDocument()
    })

    describe('... and with WIP_ENABLE_PRO_DIDACTIC_ONBOARDING enabled', () => {
      it('should return true if firebase config is true for user', () => {
        vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
          PRO_DIDACTIC_ONBOARDING_AB_TEST: 'true',
        })
        renderuseHasAccessToDidacticOnboarding([
          'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
          'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST',
        ])

        expect(screen.getByText('OUI')).toBeInTheDocument()
      })

      it('should return false if firebase config is false for user', () => {
        renderuseHasAccessToDidacticOnboarding([
          'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
          'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST',
        ])
        expect(screen.getByText('NON')).toBeInTheDocument()
      })
    })
  })
})
