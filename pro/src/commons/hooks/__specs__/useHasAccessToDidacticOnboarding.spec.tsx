import { screen } from '@testing-library/react'

import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

const TestComponent = () => {
  return <div>{useHasAccessToDidacticOnboarding() ? 'OUI' : 'NON'}</div>
}

const renderuseHasAccessToDidacticOnboarding = (
  features: string[] = [],
  userId: number = 2
) => {
  return renderWithProviders(<TestComponent />, {
    features,
    user: sharedCurrentUserFactory({ id: userId }),
  })
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
      it('should return true if user id is an even number', () => {
        renderuseHasAccessToDidacticOnboarding(
          [
            'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
            'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST',
          ],
          2
        )

        expect(screen.getByText('OUI')).toBeInTheDocument()
      })

      it('should return false if user id is an odd number', () => {
        renderuseHasAccessToDidacticOnboarding(
          [
            'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
            'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST',
          ],
          1
        )
        expect(screen.getByText('NON')).toBeInTheDocument()
      })
    })
  })
})
