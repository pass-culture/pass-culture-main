import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { ApiRequestOptions } from '@/apiClient//adage/core/ApiRequestOptions'
import { api } from '@/apiClient//api'
import { ApiError, VenueOfOffererFromSiretResponseModel } from '@/apiClient//v1'
import { ApiResult } from '@/apiClient//v1/core/ApiResult'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'

import { Offerers } from '../Offerers'

vi.mock('@/apiClient//api', () => ({
  api: {
    getVenuesOfOffererFromSiret: vi.fn(),
    createOfferer: vi.fn(),
  },
}))

const renderOfferersScreen = (
  contextValue: SignupJourneyContextValues,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Routes>
        <Route
          path="/inscription/structure/recherche"
          element={<div>Offerer screen</div>}
        />
        <Route
          path="/inscription/structure/recherche/rattachement"
          element={<Offerers />}
        />
        <Route
          path="/inscription/structure/identification"
          element={<div>Authentication screen</div>}
        />
        <Route
          path="/inscription/structure/rattachement/confirmation"
          element={<div>Confirmation screen</div>}
        />
      </Routes>
    </SignupJourneyContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche/rattachement'],
      ...options,
    }
  )
}
describe('screens:SignupJourney::Offerers', () => {
  let contextValue: SignupJourneyContextValues
  let venues: VenueOfOffererFromSiretResponseModel[]

  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Offerer Name',
        siret: '12345678933333',
        apeCode: '5610C',
        city: 'lille',
        postalCode: '59000',
        siren: '123456789',
      },
      setActivity: () => {},
      setOfferer: () => {},
    }

    venues = [
      {
        id: 0,
        siret: '12345678913333',
        name: 'venue 0',
        isPermanent: false,
      },
      {
        id: 1,
        siret: '12345678913333',
        name: 'venue 1',
        isPermanent: true,
      },
      {
        id: 2,
        siret: '12345678923333',
        name: 'venue 2',
        isPermanent: true,
      },
      {
        id: 3,
        siret: '12345678933333',
        name: 'venue 3',
        isPermanent: true,
      },
      {
        id: 4,
        siret: '12345678943333',
        name: 'venue 4',
        isPermanent: true,
      },
      {
        id: 5,
        siret: '12345678953333',
        name: 'venue 5',
        isPermanent: true,
      },
      {
        id: 6,
        siret: '12345678963333',
        name: 'venue 6',
        publicName: 'public venue 6',
        isPermanent: true,
      },
    ]

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererName: 'Offerer Name',
      offererSiren: '123456789',
      venues,
    })
  })

  it('should render component', async () => {
    renderOfferersScreen(contextValue)

    expect(
      await screen.findByText(
        'Nous avons trouvé un espace déjà inscrit comprenant le SIRET',
        { exact: false }
      )
    ).toBeInTheDocument()

    expect(screen.getByText('Offerer Name')).toBeInTheDocument()

    expect(screen.getAllByRole('listitem')).toHaveLength(4)
    expect(screen.queryByText('venue 5')).not.toBeVisible()
    expect(screen.queryByText('public venue 6')).not.toBeVisible()

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
      screen.queryByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Vous souhaitez ajouter une nouvelle structure à cet espace ?'
      )
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Retour',
      })
    ).toBeInTheDocument()
  })

  it('should render component without venue attachement', async () => {
    renderOfferersScreen(contextValue, {
      features: ['WIP_RESTRICT_VENUE_ATTACHMENT_TO_COLLECTIVITY'],
    })

    expect(
      await screen.findByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Rejoindre cet espace' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText(
        'Vous souhaitez ajouter une nouvelle structure à cet espace ?'
      )
    ).toBeInTheDocument()
  })

  it('should render component without venue creation', async () => {
    renderOfferersScreen(contextValue, {
      features: ['WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY'],
    })

    expect(
      await screen.findByRole('button', { name: 'Rejoindre cet espace' })
    ).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Vous souhaitez ajouter une nouvelle structure à cet espace ?'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).not.toBeInTheDocument()
  })

  it('should render component with venue creation/attachment to collectivities', async () => {
    renderOfferersScreen(
      {
        ...contextValue,
        offerer: { ...DEFAULT_OFFERER_FORM_VALUES, apeCode: '84.11Z' },
      },
      {
        features: [
          'WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY',
          'WIP_RESTRICT_VENUE_ATTACHMENT_TO_COLLECTIVITY',
        ],
      }
    )

    expect(
      await screen.findByRole('button', { name: 'Rejoindre cet espace' })
    ).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Vous souhaitez ajouter une nouvelle structure à cet espace ?'
      )
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Ajouter une nouvelle structure',
      })
    ).toBeInTheDocument()
  })

  it('should not display non permanent venues', async () => {
    renderOfferersScreen(contextValue)
    expect(
      await screen.findByText(
        'Nous avons trouvé un espace déjà inscrit comprenant le SIRET',
        { exact: false }
      )
    ).toBeInTheDocument()
    expect(screen.queryByText('venue 0')).not.toBeInTheDocument()
    expect(screen.queryByText('public venue 0')).not.toBeInTheDocument()
  })

  it('should not display venueListToggle', async () => {
    // toggle venues list is displayed only when venues length > 5
    venues.pop()
    renderOfferersScreen(contextValue)

    expect(await screen.findAllByRole('listitem')).toHaveLength(5)
    expect(screen.queryByText('venue 5')).toBeVisible()

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
    expect(screen.queryByText('venue 5')).not.toBeVisible()
    expect(screen.queryByText('public venue 6')).not.toBeVisible()

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
    expect(screen.queryByText('venue 5')).toBeVisible()
    expect(screen.queryByText('public venue 6')).toBeVisible()

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

  it('should redirect only local authority to offerer authentication on add offerer button click', async () => {
    const contextValueForLocalAuthority = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Trifoulli les Oies',
        siret: '12345678933333',
        apeCode: '84.11Z',
      },
      setActivity: () => {},
      setOfferer: () => {},
    }

    renderOfferersScreen(contextValueForLocalAuthority)

    expect(
      await screen.findByText(
        'Nous avons trouvé un espace déjà inscrit comprenant le SIRET',
        { exact: false }
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
        'Nous avons trouvé un espace déjà inscrit comprenant le SIRET',
        { exact: false }
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
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValueOnce(
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

  it('should display add a venue button for local authority', async () => {
    const contextValueForLocalAuthority = {
      activity: null,
      offerer: {
        ...DEFAULT_OFFERER_FORM_VALUES,
        name: 'Trifoulli les Oies',
        siret: '12345678933333',
        apeCode: '84.11Z',
      },
      setActivity: () => {},
      setOfferer: () => {},
    }

    renderOfferersScreen(contextValueForLocalAuthority)
    expect(
      await screen.findByText('Ajouter une nouvelle structure')
    ).toBeInTheDocument()
  })

  describe('modal handling', () => {
    it('should display confirmation dialog when user want to be linked to the structure', async () => {
      renderOfferersScreen(contextValue)

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText(
          'Êtes-vous sûr de vouloir rejoindre cet espace ?'
        )
      ).toBeInTheDocument()
    })

    it('should not link offerer to user when they cancel', async () => {
      renderOfferersScreen(contextValue)

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText(
          'Êtes-vous sûr de vouloir rejoindre cet espace ?'
        )
      ).toBeInTheDocument()

      await userEvent.click(await screen.findByText('Annuler'))

      expect(
        screen.queryByText('Êtes-vous sûr de vouloir rejoindre cet espace ?')
      ).not.toBeInTheDocument()
      expect(api.createOfferer).not.toHaveBeenCalled()
    })

    it('should link offerer to user when they confirm', async () => {
      renderOfferersScreen(contextValue)
      vi.spyOn(api, 'createOfferer').mockResolvedValue(expect.anything())

      await userEvent.click(await screen.findByText('Rejoindre cet espace'))

      expect(
        await screen.findByText(
          'Êtes-vous sûr de vouloir rejoindre cet espace ?'
        )
      ).toBeInTheDocument()

      await userEvent.click(
        await screen.findByRole('button', { name: 'Rejoindre cet espace' })
      )

      expect(api.createOfferer).toHaveBeenCalledWith({
        city: 'lille',
        name: 'Offerer Name',
        postalCode: '59000',
        siren: '123456789',
      })
      expect(await screen.findByText('Confirmation screen')).toBeInTheDocument()
    })
  })
})
