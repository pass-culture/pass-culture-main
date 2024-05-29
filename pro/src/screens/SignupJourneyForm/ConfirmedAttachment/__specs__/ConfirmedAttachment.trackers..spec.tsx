import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

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
        categorieJuridiqueUniteLegale: '',
      }
    )
  })
})
