import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ConfirmedAttachment } from '..'

const mockLogEvent = jest.fn()

const renderConfirmedAttachmentScreen = (
  contextValue: ISignupJourneyContext
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <ConfirmedAttachment />
    </SignupJourneyContext.Provider>,
    {
      storeOverrides,
    }
  )
}
describe('ConfirmedAttachment trackers', () => {
  let contextValue: ISignupJourneyContext

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
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
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
