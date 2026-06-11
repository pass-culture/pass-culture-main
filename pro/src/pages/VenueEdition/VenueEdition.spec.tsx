import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { api, apiNew } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

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
  const translatedContext =
    context === 'adage' ? '/page-collective' : '/page-partenaire'
  const initialPath = `/partenaire${translatedContext}/edition`

  return renderWithProviders(
    <Routes>
      <Route path="/partenaire/*">
        <Route path="*" element={<VenueEdition />} />
      </Route>
      <Route path="/accueil" element={<h1>Home</h1>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [initialPath],
      ...{
        storeOverrides: {
          user: {
            selectedAdminOfferer: {
              ...defaultGetOffererResponseModel,
              id: 100,
            },
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
  useNavigate: () => mockUseNavigate,
}))

const baseVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  publicName: 'Cinéma des iles',
  isPermanent: true,
}

describe('VenueEdition', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getVenue').mockResolvedValue(baseVenue)
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'getVenuesEducationalStatuses').mockResolvedValue({
      statuses: [],
    })
    mockUseNavigate.mockClear()
  })

  describe('about title (main heading / h1)', () => {
    it('should display "Page sur l’application" for a permanent venue & individual partner page', async () => {
      renderVenueEdition({ context: 'partnerPage' })

      await screen.findByRole('heading', { name: 'Cinéma des iles' })

      expect(
        screen.getByRole('heading', {
          name: 'Page sur l’application',
          level: 1,
        })
      ).toBeInTheDocument()
    })

    it('should display "Page dans ADAGE" for a collective partner page', async () => {
      renderVenueEdition({ context: 'adage' })

      await screen.findByRole('heading', { name: 'Cinéma des iles' })

      expect(
        screen.getByRole('heading', { name: 'Page dans ADAGE', level: 1 })
      ).toBeInTheDocument()
    })
  })

  it('should call getVenue and display venue name as a heading (h2)', async () => {
    renderVenueEdition()

    const venuePublicName = await screen.findByRole('heading', {
      name: 'Cinéma des iles',
    })
    expect(apiNew.getVenue).toHaveBeenCalledWith({
      path: { venue_id: defaultGetVenue.id },
    })
    expect(venuePublicName).toBeInTheDocument()
  })

  describe('about venue / partner page selection', () => {
    it('should not let choose an other partner page when there is only one partner page', async () => {
      const options: RenderWithProvidersOptions = {
        storeOverrides: {
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

      await screen.findByRole('heading', { name: 'Cinéma des iles' })

      expect(
        screen.queryByLabelText('Sélectionnez votre page partenaire')
      ).not.toBeInTheDocument()
    })
  })
})
