import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import type {
  GetVenueResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import * as utils from '@/commons/utils/savedPartnerPageVenueId'

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
      <Route path="/structures/:offererId/lieux/:venueId/*">
        <Route path="*" element={<VenueEdition />} />
      </Route>
      <Route path="/accueil" element={<h1>Home</h1>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialPath],
      ...options,
    }
  )
}
const mockUseNavigate = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useParams: () => ({
    offererId: '1',
    venueId: defaultGetVenue.id,
  }),
  useNavigate: () => mockUseNavigate,
}))

const mockDispatch = vi.fn()
vi.mock('react-redux', async () => {
  const actual = await vi.importActual('react-redux')
  return {
    ...actual,
    useDispatch: () => mockDispatch,
  }
})

const selectCurrentOffererId = vi.hoisted(() => vi.fn())
vi.mock('@/commons/store/offerer/selectors', async () => ({
  ...(await vi.importActual('@/commons/store/offerer/selectors')),
  selectCurrentOffererId,
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

const FIRST_VENUE = { id: 1, name: 'First Venue' }
const SECOND_VENUE = { id: 2, name: 'Second Venue' }
const mockDataVenues: { venues: VenueListItemResponseModel[] } = {
  venues: [
    makeVenueListItem({
      id: FIRST_VENUE.id,
      name: FIRST_VENUE.name,
      isPermanent: true,
      hasCreatedOffer: true,
    }),
    makeVenueListItem({
      id: SECOND_VENUE.id,
      name: SECOND_VENUE.name,
      isPermanent: true,
      hasCreatedOffer: true,
    }),
  ],
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
    selectCurrentOffererId.mockReturnValue(defaultGetOffererResponseModel.id)
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
      vi.spyOn(api, 'getVenues').mockResolvedValue(mockDataVenues)
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire'),
        FIRST_VENUE.id.toString()
      )
      expect(screen.getByText(FIRST_VENUE.name)).toBeInTheDocument()

      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire'),
        SECOND_VENUE.id.toString()
      )
      expect(screen.getByText(SECOND_VENUE.name)).toBeInTheDocument()
    })

    it('should save the venue id in local storage on selection', async () => {
      const setSavedPartnerPageVenueId = vi.fn()
      vi.spyOn(utils, 'setSavedPartnerPageVenueId').mockImplementation(() => ({
        setSavedPartnerPageVenueId,
      }))
      vi.spyOn(api, 'getVenues').mockResolvedValue(mockDataVenues)

      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      const selectedVenueId = SECOND_VENUE.id.toString()
      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire'),
        selectedVenueId
      )

      expect(utils.setSavedPartnerPageVenueId).toHaveBeenCalled()
      vi.spyOn(utils, 'setSavedPartnerPageVenueId').mockReset()

      // We also expect dispatch to be called to update
      // side nav partner page link.
      expect(mockDispatch).toHaveBeenCalledWith(
        expect.objectContaining({
          payload: selectedVenueId,
        })
      )
    })

    it('should not let choose an other partner page when there is only one partner page', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
        venues: [
          makeVenueListItem({
            id: FIRST_VENUE.id,
            publicName: FIRST_VENUE.name,
          }),
          makeVenueListItem({
            id: SECOND_VENUE.id,
            publicName: SECOND_VENUE.name,
            isPermanent: false,
            hasCreatedOffer: false,
          }),
        ],
      })
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.queryByLabelText('Sélectionnez votre page partenaire')
      ).not.toBeInTheDocument()
    })

    it('should not let choose an other partner page when on adress page', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(mockDataVenues)
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
