import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { OnboardingFormNavigationAction } from '@/components/SignupJourneyFormLayout/constants'

import { Offerers } from '../Offerers'

const mockLogEvent = vi.fn()
vi.mock('@/apiClient/api', () => ({
  api: {
    getVenuesOfOffererFromSiret: vi.fn(),
  },
}))

const renderOfferersScreen = (contextValue: SignupJourneyContextValues) => {
  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Offerers />
    </SignupJourneyContext.Provider>,
    { user: sharedCurrentUserFactory() }
  )
}
describe('Offerers trackers', () => {
  let contextValue: SignupJourneyContextValues

  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Offerer Name',
        siret: '12345678933334',
      },
      setActivity: () => {},
      setOfferer: () => {},
    }

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererName: 'Offerer Name',
      offererSiren: '123456789',
      venues: [
        {
          id: 0,
          siret: '12345678913334',
          name: 'venue 0',
          isPermanent: false,
        },
      ],
    })

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should track displaying the confirmation dialog', async () => {
    renderOfferersScreen(contextValue)

    await userEvent.click(await screen.findByText('Rejoindre cet espace'))

    expect(
      await screen.findByText('Êtes-vous sûr de vouloir rejoindre cet espace ?')
    ).toBeInTheDocument()

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/',
        to: 'LinkModal',
        used: OnboardingFormNavigationAction.LinkModalActionButton,
      }
    )
  })

  it('should track closing the not link offerer modal', async () => {
    renderOfferersScreen(contextValue)

    await userEvent.click(await screen.findByText('Rejoindre cet espace'))

    expect(
      await screen.findByText('Êtes-vous sûr de vouloir rejoindre cet espace ?')
    ).toBeInTheDocument()

    await userEvent.click(await screen.findByText('Annuler'))

    // The first one is the one called when opening the modal
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: 'LinkModal',
        to: '/',
        used: OnboardingFormNavigationAction.LinkModalActionButton,
      }
    )
  })
})
