import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
  defaultVenueProvider,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { VenueEdition } from '../VenueEdition'

interface VenueEditionTestProps {
  context?: 'adage' | 'partnerPage' | 'address'
  options?: RenderWithProvidersOptions
}

const renderVenueEdition = ({
  context = 'address',
  options,
}: VenueEditionTestProps = {}) => {
  const offererId = defaultGetOffererResponseModel.id
  const venueId = defaultGetVenue.id
  const translatedContext =
    context === 'adage'
      ? '/collectif'
      : context === 'partnerPage'
        ? '/page-partenaire'
        : ''
  const initialPath = `/structures/${offererId}/lieux/${venueId}${translatedContext}/edition`

  return renderWithProviders(
    <Routes>
      <Route
        path="/structures/:offererId/lieux/:venueId/*"
        element={<VenueEdition />}
      />
      <Route path="/accueil" element={<h1>Home</h1>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialPath],
      ...options,
    }
  )
}

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    offererId: '1',
    venueId: defaultGetVenue.id,
  }),
  useNavigate: () => vi.fn(),
}))

const baseVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  publicName: 'Cinéma des iles',
  dmsToken: 'dms-token-12345',
  isPermanent: true,
}

const notValidatedVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  isPermanent: false,
}

describe('VenueEdition', () => {
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
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'getVenuesEducationalStatuses').mockResolvedValue({
      statuses: [],
    })
    vi.spyOn(api, 'getEducationalPartners').mockResolvedValue({ partners: [] })
  })

  describe('about title (main heading / h1)', () => {
    it('should display "Page sur l’application" for a permanent venue & individual partner page', async () => {
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.getByRole('heading', { name: 'Page sur l’application' })
      ).toBeInTheDocument()
    })

    it('should display "Page adresse" for a non-permanent venue & individual partner page', async () => {
      renderVenueEdition({ context: 'address' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(screen.getByText('Page adresse')).toBeInTheDocument()
    })

    it('should display "Page dans ADAGE" for a collective partner page', async () => {
      renderVenueEdition({ context: 'adage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(screen.getByText('Page dans ADAGE')).toBeInTheDocument()
    })
  })

  it('should call getVenue and display venue name as a heading (h2)', async () => {
    renderVenueEdition()

    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(api.getVenue).toHaveBeenCalledWith(defaultGetVenue.id)
    expect(venuePublicName).toBeInTheDocument()
  })

  describe('about venue / partner page selection', () => {
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
      renderVenueEdition({ context: 'partnerPage' })

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
            hasPartnerPage: false,
          },
        ],
      })
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.queryByLabelText('Sélectionnez votre page partenaire')
      ).not.toBeInTheDocument()
    })

    it('should not let choose an other partner page when on adress page', async () => {
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
      renderVenueEdition({ context: 'address' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(screen.getByText('Page adresse')).toBeInTheDocument()
      expect(
        screen.queryByLabelText('Sélectionnez votre page partenaire')
      ).not.toBeInTheDocument()
    })

    it('should display the selector only for new navigation', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValue(notValidatedVenue)
      renderVenueEdition()

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.queryByText('Page sur l’application')
      ).not.toBeInTheDocument()
    })
  })

  describe('about tab navigation', () => {
    it('should not display tab navigation for permanent venues', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
        ...baseVenue,
        isPermanent: true,
      })
      renderVenueEdition({ options: { user: sharedCurrentUserFactory() } })
      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(screen.queryByText('Pour le grand public')).not.toBeInTheDocument()
      expect(screen.queryByText('Pour les enseignants')).not.toBeInTheDocument()
    })

    it('should display tab navigation for not permanent venues', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
        ...baseVenue,
        isPermanent: false,
      })
      renderVenueEdition()
      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(screen.getByText('Pour le grand public')).toBeInTheDocument()
      expect(screen.getByText('Pour les enseignants')).toBeInTheDocument()
    })
  })

  // TODO: This should be moved in VenueEditionFormScreen.spec.tsx > on edition (VenueEditionForm)
  describe('about opening hours & accessibility', () => {
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

    it('should display the acces libre callout for permanent venues', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
        ...baseVenue,
        isPermanent: true,
      })
      renderVenueEdition({ context: 'address' })

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
      renderVenueEdition({ context: 'address' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.queryByText(
          'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr'
        )
      ).not.toBeInTheDocument()
    })
  })

  // TODO: This test is probably deprecated, and outputs as a false positive,
  // since "Barème de remboursement" is rendered in a sub component that is not
  // used in VenueEdition.
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
})
