import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { DEFAULT_OFFERER_FORM_VALUES } from 'components/SignupJourneyForm/Offerer/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'

import { ConfirmedAttachment } from '../ConfirmedAttachment'

const mockLogEvent = vi.fn()

const renderConfirmedAttachmentScreen = (
  contextValue: SignupJourneyContextValues
) => {
  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <ConfirmedAttachment />
    </SignupJourneyContext.Provider>,
    { user: sharedCurrentUserFactory() }
  )
}
describe('ConfirmedAttachment trackers', () => {
  let contextValue: SignupJourneyContextValues

  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Offerer Name',
        siret: '12345678933333',
      },
      setActivity: () => {},
      setOfferer: () => {},
    }
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })
  it('should redirect user on offerer page on continue button click', async () => {
    renderConfirmedAttachmentScreen(contextValue)

    await userEvent.click(screen.getByText('Accéder à votre espace'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ONBOARDING_FORM_NAVIGATION,
      {
        from: '/',
        to: SIGNUP_JOURNEY_STEP_IDS.COMPLETED,
        used: OnboardingFormNavigationAction.WaitingLinkButton,
      }
    )
  })
})
