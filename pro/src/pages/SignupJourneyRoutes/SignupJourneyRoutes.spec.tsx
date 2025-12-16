import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'
import createFetchMock from 'vitest-fetch-mock'

import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { Component as SignupJourneyRoutes } from './SignupJourneyRoutes'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderOffererAuthenticationScreen = (
  contextValue: SignupJourneyContextValues,
  initialRoute = '/inscription/structure/recherche',
  features: string[] = []
) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/recherche"
            element={<div>Offerer screen</div>}
          />
          <Route
            path="/inscription/structure/identification"
            element={<div>Identification screen</div>}
          />
        </Routes>
        <SignupJourneyRoutes />
      </SignupJourneyContext.Provider>
      <SnackBarContainer />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialRoute],
      features,
    }
  )
}

describe('SignupJourneyRoutes', () => {
  let contextValue: SignupJourneyContextValues
  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        siret: '123 456 789 33333',
        name: 'Test name',
        street: '3 Rue de Valois',
        city: 'Paris',
        latitude: 0,
        longitude: 0,
        postalCode: '75001',
        publicName: '',
        isOpenToPublic: 'true',
      },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress: null,
      setInitialAddress: noop,
    }
  })
  it('should redirect to offerer screen if there is no offerer siret', () => {
    contextValue.offerer = DEFAULT_OFFERER_FORM_VALUES
    renderOffererAuthenticationScreen(
      contextValue,
      '/inscription/structure/identification'
    )
    expect(screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  it('should redirect to offerer screen if there is no offerer siren', () => {
    contextValue.offerer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      siret: '12345678933333',
      siren: '',
    }
    renderOffererAuthenticationScreen(
      contextValue,
      '/inscription/structure/identification'
    )
    expect(screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  it('should not redirect to offerer screen on offerer screen', () => {
    contextValue.offerer = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      siret: '',
      siren: '',
    }
    renderOffererAuthenticationScreen(contextValue)
    expect(screen.queryByText('Identification')).not.toBeInTheDocument()
    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })
})
