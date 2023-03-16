import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { ApiRequestOptions } from 'apiClient/adage/core/ApiRequestOptions'
import { api } from 'apiClient/api'
import { ApiError, VenueOfOffererFromSiretResponseModel } from 'apiClient/v1'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Offerers } from '..'

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
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Routes>
        <Route
          path="/parcours-inscription/structure"
          element={<div>Offerer screen</div>}
        />
        <Route path="/parcours-inscription/structures" element={<Offerers />} />
        <Route
          path="/parcours-inscription/authentification"
          element={<div>Authentication screen</div>}
        />
      </Routes>
    </SignupJourneyContext.Provider>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription/structures'],
    }
  )
}
describe('screens:SignupJourney::Offerers', () => {
  let contextValue: ISignupJourneyContext
  let venues: VenueOfOffererFromSiretResponseModel[]

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

    venues = [
      {
        id: '1',
        siret: '12345678913333',
        name: 'venue 1',
      },
      {
        id: '2',
        siret: '12345678923333',
        name: 'venue 2',
      },
      {
        id: '3',
        siret: '12345678933333',
        name: 'venue 3',
      },
      {
        id: '4',
        siret: '12345678943333',
        name: 'venue 4',
      },
      {
        id: '5',
        siret: '12345678953333',
        name: 'venue 5',
      },
      {
        id: '6',
        siret: '12345678963333',
        name: 'venue 6',
      },
    ]

    jest.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererName: 'Offerer Name',
      offererSiren: '123456789',
      venues,
    })
  })

  it('should render component', async () => {
    renderOfferersScreen(contextValue)

    expect(
      await screen.findByRole('heading', {
        level: 1,
        name: 'Nous avons trouvé un espace déjà inscrit sur le pass Culture et incluant ce SIRET.',
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        level: 4,
        name: 'Rejoignez-le si votre structure se trouve dans la liste.',
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        level: 4,
        name: 'Offerer Name - 123 456 789',
      })
    ).toBeInTheDocument()

    expect(screen.getAllByRole('listitem')).toHaveLength(4)
    expect(screen.queryByText('venue 5')).not.toBeVisible()
    expect(screen.queryByText('venue 6')).not.toBeVisible()

    expect(
      await screen.findByRole('button', {
        name: 'Afficher plus de structures',
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Afficher moins de structures',
      })
    ).not.toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Rejoindre cet espace' })
    ).toBeInTheDocument()

    expect(
      await screen.queryByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        level: 4,
        name: 'Votre structure ne se trouve pas dans cette liste ?',
      })
    ).toBeInTheDocument()

    expect(
      await screen.queryByRole('button', {
        name: 'Retour',
      })
    ).toBeInTheDocument()
  })

  it('should not display venueListToggle', async () => {
    // toggle venues list is displayed only when venues length > 5
    venues.pop()
    renderOfferersScreen(contextValue)

    expect(await screen.findAllByRole('listitem')).toHaveLength(5)
    expect(await screen.queryByText('venue 5')).toBeVisible()

    expect(
      screen.queryByRole('button', {
        name: 'Afficher plus de structures',
      })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Afficher moins de structures',
      })
    ).not.toBeInTheDocument()
  })

  it('should toggle venues list', async () => {
    renderOfferersScreen(contextValue)

    expect(await screen.findAllByRole('listitem')).toHaveLength(4)
    expect(await screen.queryByText('venue 5')).not.toBeVisible()
    expect(await screen.queryByText('venue 6')).not.toBeVisible()

    await userEvent.click(screen.getByText('Afficher plus de structures'))

    await waitFor(() => {
      expect(
        screen.queryByRole('button', {
          name: 'Afficher plus de structures',
        })
      ).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('button', {
        name: 'Afficher moins de structures',
      })
    ).toBeInTheDocument()

    expect(await screen.findAllByRole('listitem')).toHaveLength(6)
    expect(await screen.queryByText('venue 5')).toBeVisible()
    expect(await screen.queryByText('venue 6')).toBeVisible()

    await userEvent.click(screen.getByText('Afficher moins de structures'))

    expect(
      screen.getByRole('button', {
        name: 'Afficher plus de structures',
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Afficher moins de structures',
      })
    ).not.toBeInTheDocument()
  })

  it('should redirect to offerer authentication on add offerer button click', async () => {
    renderOfferersScreen(contextValue)

    expect(
      await screen.findByText(
        'Nous avons trouvé un espace déjà inscrit sur le pass Culture et incluant ce SIRET.'
      )
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    )

    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should redirect to offerer on back button click', async () => {
    renderOfferersScreen(contextValue)

    expect(
      await screen.findByText(
        'Nous avons trouvé un espace déjà inscrit sur le pass Culture et incluant ce SIRET.'
      )
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Retour',
      })
    )

    expect(screen.getByText('Offerer screen')).toBeInTheDocument()
  })

  it('should redirect user if there is no siret', async () => {
    jest.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 404,
          body: [{ error: ['No SIRET found'] }],
        } as ApiResult,
        ''
      )
    )
    renderOfferersScreen(contextValue)
    expect(await screen.findByText('Offerer screen')).toBeInTheDocument()
  })
})
