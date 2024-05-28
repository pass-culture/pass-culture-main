import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
  defaultVenueProvider,
} from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { VenueEdition } from '../VenueEdition'

const renderVenueEdition = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/structures/:offererId/lieux/:venueId/*"
        element={<VenueEdition />}
      />
      <Route path="/accueil" element={<h1>Home</h1>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory({
        // a date in the past to have the new interface
        navState: { newNavDate: '2002-07-29T12:18:43.087097Z' },
      }),

      initialRouterEntries: [
        `/structures/${defaultGetOffererResponseModel.id}/lieux/${defaultGetVenue.id}/edition`,
      ],
      ...options,
    }
  )
}

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    venueId: defaultGetVenue.id,
  }),
  useNavigate: vi.fn(),
}))

const baseVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  publicName: 'Cinéma des iles',
  dmsToken: 'dms-token-12345',
  isPermanent: true,
}

describe('route VenueEdition', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(baseVenue)
    vi.spyOn(api, 'listVenueProviders').mockResolvedValue({
      venue_providers: [defaultVenueProvider],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    vi.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
    vi.spyOn(api, 'listOffers').mockResolvedValue([])
  })

  it('should call getVenue and display Venue Form screen on success', async () => {
    renderVenueEdition()

    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(api.getVenue).toHaveBeenCalledWith(defaultGetVenue.id)
    expect(venuePublicName).toBeInTheDocument()
  })

  it('should display the individual title', async () => {
    renderVenueEdition()

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'Page sur l’application' })
    ).toBeInTheDocument()
  })

  it('should display the collective title', async () => {
    renderVenueEdition({
      initialRouterEntries: [
        `/structures/${defaultGetOffererResponseModel.id}/lieux/${defaultGetVenue.id}/edition/collectif`,
      ],
    })

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(screen.getByText('Page dans ADAGE')).toBeInTheDocument()
  })

  it('should display the addresse title', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      isPermanent: false,
    })
    renderVenueEdition({
      initialRouterEntries: [
        `/structures/${defaultGetOffererResponseModel.id}/lieux/${defaultGetVenue.id}`,
      ],
    })

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(screen.getByText('Page adresse')).toBeInTheDocument()
  })

  it('should let choose an other partner page', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          id: 13,
          publicName: 'Mon lieu de malheur',
        },
        {
          ...defaultGetOffererVenueResponseModel,
          id: 666,
          publicName: 'Mon lieu diabolique',
        },
      ],
    })
    renderVenueEdition()

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    await userEvent.selectOptions(
      screen.getByLabelText('Sélectionnez votre page partenaire'),
      '13'
    )
    expect(screen.getByText('Mon lieu de malheur')).toBeInTheDocument()

    await userEvent.selectOptions(
      screen.getByLabelText('Sélectionnez votre page partenaire'),
      '666'
    )
    expect(screen.getByText('Mon lieu diabolique')).toBeInTheDocument()
  })

  it('should not let choose an other partner page when there is only one partner page', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
      ...defaultGetOffererResponseModel,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          id: 13,
          publicName: 'Mon lieu de malheur',
        },
        {
          ...defaultGetOffererVenueResponseModel,
          id: 666,
          publicName: 'Mon lieu diabolique',
          isPermanent: false,
        },
      ],
    })
    renderVenueEdition()

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(
      screen.queryByLabelText('Sélectionnez votre page partenaire')
    ).not.toBeInTheDocument()
  })

  it('should not let choose an other partner page when on adress page', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...baseVenue,
      isPermanent: false,
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          id: 13,
          publicName: 'Mon lieu de malheur',
        },
        {
          ...defaultGetOffererVenueResponseModel,
          id: 666,
          publicName: 'Mon lieu diabolique',
        },
      ],
    })
    renderVenueEdition()

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(screen.getByText('Page adresse')).toBeInTheDocument()
    expect(
      screen.queryByLabelText('Sélectionnez votre page partenaire')
    ).not.toBeInTheDocument()
  })

  it('should display the selector only for new navigation', async () => {
    renderVenueEdition({
      user: sharedCurrentUserFactory({
        // a date in the futur to not have the new interface
        navState: { newNavDate: '2225-07-29T12:18:43.087097Z' },
      }),
    })

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
  })

  it('should check none accessibility', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      siret: undefined,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      audioDisabilityCompliant: false,
      motorDisabilityCompliant: false,
    })

    renderVenueEdition()

    await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })

    expect(
      screen.getByLabelText('Non accessible', { exact: false })
    ).toBeChecked()
  })

  it('should not check none accessibility if every accessibility parameters are null', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      visualDisabilityCompliant: null,
      mentalDisabilityCompliant: null,
      audioDisabilityCompliant: null,
      motorDisabilityCompliant: null,
    })

    renderVenueEdition()

    await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })

    expect(
      screen.getByLabelText('Non accessible', { exact: false })
    ).not.toBeChecked()
  })

  it('should not render reimbursement fields when FF bank details is enabled and venue has no siret', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      siret: '11111111111111',
    })

    renderVenueEdition()

    await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })

    expect(
      screen.queryByText(/Barème de remboursement/)
    ).not.toBeInTheDocument()
  })

  it('should display the acces libre callout for permanent venues', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      isPermanent: true,
    })
    renderVenueEdition({
      initialRouterEntries: [
        `/structures/${defaultGetOffererResponseModel.id}/lieux/${defaultGetVenue.id}`,
      ],
    })

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(
      screen.getByText(
        'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr'
      )
    ).toBeInTheDocument()
  })

  it('should not display the acces libre callout for non permanent venues', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      isPermanent: false,
    })
    renderVenueEdition({
      initialRouterEntries: [
        `/structures/${defaultGetOffererResponseModel.id}/lieux/${defaultGetVenue.id}`,
      ],
    })

    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(
      screen.queryByText(
        'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr'
      )
    ).not.toBeInTheDocument()
  })

  it('should not display tab navigation for permanent venues', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      isPermanent: true,
    })
    renderVenueEdition({
      user: sharedCurrentUserFactory({
        navState: { newNavDate: '2002-07-29T12:18:43.087097Z' },
      }),
    })
    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(screen.queryByText('Pour le grand public')).not.toBeInTheDocument()
    expect(screen.queryByText('Pour les enseignants')).not.toBeInTheDocument()
  })

  it('should display tab navigation for not permanent venues', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
      ...baseVenue,
      isPermanent: false,
    })
    renderVenueEdition({})
    await waitForElementToBeRemoved(screen.getByTestId('spinner'))

    expect(screen.getByText('Pour le grand public')).toBeInTheDocument()
    expect(screen.getByText('Pour les enseignants')).toBeInTheDocument()
  })
})
