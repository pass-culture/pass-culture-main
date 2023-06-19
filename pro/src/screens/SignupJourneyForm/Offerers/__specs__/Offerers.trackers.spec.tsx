import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Offerers } from '..'

const mockLogEvent = jest.fn()
jest.mock('apiClient/api', () => ({
  api: {
    getVenuesOfOffererFromSiret: jest.fn(),
  },
}))

const renderOfferersScreen = (contextValue: ISignupJourneyContext) => {
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
      <Offerers />
    </SignupJourneyContext.Provider>,
    {
      storeOverrides,
    }
  )
}
describe('Offerers trackers', () => {
  let contextValue: ISignupJourneyContext

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

    jest.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
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

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
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
        categorieJuridiqueUniteLegale: '',
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
        categorieJuridiqueUniteLegale: '',
      }
    )
  })
})
