import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { setSavedPartnerPageVenueId } from '@/commons/utils/savedPartnerPageVenueId'

import { VenueEdition } from './VenueEdition'

interface VenueEditionTestProps {
  context?: 'adage' | 'partnerPage' | 'address'
  options?: RenderWithProvidersOptions
}

const FIRST_VENUE = {
  id: 1,
  name: 'Venue Name 1',
  publicName: 'Venue Public Name 1',
}
const SECOND_VENUE = {
  id: 2,
  name: 'Venue Name 2',
  publicName: 'Venue Public Name 2',
}

const renderVenueEdition = ({
  context,
  options,
}: VenueEditionTestProps = {}) => {
  const offererId = defaultGetOffererResponseModel.id
  const venueId = defaultGetVenue.id
  const translatedContext =
    context === 'adage' ? '/collectif' : '/page-partenaire'
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
      ...{
        storeOverrides: {
          offerer: {
            currentOfferer: { ...defaultGetOffererResponseModel, id: 100 },
          },
          user: {
            selectedPartnerVenue: makeGetVenueResponseModel({
              id: FIRST_VENUE.id,
              name: FIRST_VENUE.name,
              publicName: FIRST_VENUE.publicName,
            }),
            venues: [
              makeVenueListItemLiteResponseModel({
                id: FIRST_VENUE.id,
                name: FIRST_VENUE.name,
                publicName: FIRST_VENUE.publicName,
              }),
              makeVenueListItemLiteResponseModel({
                id: SECOND_VENUE.id,
                name: SECOND_VENUE.name,
                publicName: SECOND_VENUE.publicName,
              }),
            ],
          },
        },
        ...options,
      },
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

vi.mock('@/commons/utils/savedPartnerPageVenueId', async () => {
  const actual = await vi.importActual<
    typeof import('@/commons/utils/savedPartnerPageVenueId')
  >('@/commons/utils/savedPartnerPageVenueId')
  return {
    ...actual,
    setSavedPartnerPageVenueId: vi.fn(),
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
  isPermanent: true,
}

describe('VenueEdition', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({
          id: FIRST_VENUE.id,
          hasCreatedOffer: true,
          isPermanent: true,
          name: FIRST_VENUE.name,
          publicName: FIRST_VENUE.publicName,
        }),
        makeVenueListItem({
          id: SECOND_VENUE.id,
          hasCreatedOffer: true,
          isPermanent: true,
          name: SECOND_VENUE.name,
          publicName: SECOND_VENUE.publicName,
        }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(baseVenue)
    vi.spyOn(api, 'listVenueProviders').mockResolvedValue({
      venueProviders: [defaultVenueProvider],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    vi.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
    vi.spyOn(api, 'listOffers').mockResolvedValue([])
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'getVenuesEducationalStatuses').mockResolvedValue({
      statuses: [],
    })
    selectCurrentOffererId.mockReturnValue(defaultGetOffererResponseModel.id)
    mockUseNavigate.mockClear()
    vi.mocked(setSavedPartnerPageVenueId).mockClear()
  })

  describe('about title (main heading / h1)', () => {
    it('should display "Page sur l’application" for a permanent venue & individual partner page', async () => {
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.getByRole('heading', { name: 'Page sur l’application' })
      ).toBeInTheDocument()
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
    beforeEach(() => {
      localStorage.removeItem('PASS_CULTURE_HAS_SEEN_VOLUNTEERING_SECTION')
    })
    it('should let choose an other partner page', async () => {
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire'),
        FIRST_VENUE.id.toString()
      )
      expect(screen.getByText(FIRST_VENUE.publicName)).toBeInTheDocument()

      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire'),
        SECOND_VENUE.id.toString()
      )
      expect(screen.getByText(SECOND_VENUE.publicName)).toBeInTheDocument()
    })

    it('should save the venue id in local storage on selection', async () => {
      const { store } = renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      const selectedVenueId = SECOND_VENUE.id.toString()
      await userEvent.selectOptions(
        screen.getByLabelText('Sélectionnez votre page partenaire'),
        selectedVenueId
      )

      expect(store.getState().nav.selectedPartnerPageId).toBe(selectedVenueId)
    })

    it('should not let choose an other partner page when there is only one partner page', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [
          makeVenueListItem({
            id: FIRST_VENUE.id,
            name: FIRST_VENUE.name,
            publicName: FIRST_VENUE.publicName,
          }),
          makeVenueListItem({
            id: SECOND_VENUE.id,
            name: SECOND_VENUE.name,
            publicName: SECOND_VENUE.publicName,
            isPermanent: false,
            hasCreatedOffer: false,
          }),
        ],
      })

      const options: RenderWithProvidersOptions = {
        storeOverrides: {
          offerer: {
            currentOfferer: { ...defaultGetOffererResponseModel, id: 100 },
          },
          user: {
            selectedPartnerVenue: makeGetVenueResponseModel({
              id: FIRST_VENUE.id,
              name: FIRST_VENUE.name,
              publicName: FIRST_VENUE.publicName,
            }),
            venues: [],
          },
        },
      }

      renderVenueEdition({ context: 'partnerPage', options })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.queryByLabelText('Sélectionnez votre page partenaire')
      ).not.toBeInTheDocument()
    })

    it('should set HAS_SEEN_VOLUNTEERING_SECTION to true when visiting the partner page', async () => {
      renderVenueEdition({ context: 'partnerPage' })

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        localStorage.getItem('PASS_CULTURE_HAS_SEEN_VOLUNTEERING_SECTION')
      ).toBe('true')
    })
  })

  // TODO: This should be moved in VenueEditionFormScreen.spec.tsx > on edition (VenueEditionForm)
  describe('about opening hours & accessibility', () => {
    it('should check none accessibility', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValueOnce({
        ...baseVenue,
        siret: null,
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
      renderVenueEdition()

      await waitForElementToBeRemoved(screen.getByTestId('spinner'))

      expect(
        screen.getByText(
          /Complétez les modalités d'accessibilité de votre établissement sur acceslibre.beta.gouv.fr/
        )
      ).toBeInTheDocument()
    })
  })
})
