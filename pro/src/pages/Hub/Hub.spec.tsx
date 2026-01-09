import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { VenueListItemResponseModel } from '@/apiClient/v1'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Hub } from './Hub'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
    signout: vi.fn(),
  },
}))

const renderHub: RenderComponentFunction<
  void,
  void,
  { venues: VenueListItemResponseModel[] | null }
> = ({ venues }) => {
  return renderWithProviders(<Hub />, {
    storeOverrides: {
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 100 },
        currentOffererName: getOffererNameFactory({ id: 100 }),
        offererNames: [
          getOffererNameFactory({ id: 100 }),
          getOffererNameFactory({ id: 200 }),
        ],
      },
      user: {
        access: 'full',
        currentUser: sharedCurrentUserFactory(),
        selectedVenue: null,
        venues,
      },
    },
    initialRouterEntries: ['/hub'],
  })
}

describe('Hub', () => {
  const venuesBase = [
    makeVenueListItem({ id: 101, name: 'Venue A', managingOffererId: 100 }),
    makeVenueListItem({ id: 102, name: 'Venue B', managingOffererId: 100 }),
    makeVenueListItem({ id: 201, name: 'Venue C', managingOffererId: 200 }),
  ]

  const venuesWithMoreThanFour = [
    makeVenueListItem({
      id: 101,
      name: 'Théâtre du Soleil',
      managingOffererId: 100,
    }),
    makeVenueListItem({
      id: 102,
      name: 'Café des Arts',
      managingOffererId: 100,
    }),
    makeVenueListItem({
      id: 103,
      name: 'Cinéma Lumière',
      managingOffererId: 100,
    }),
    makeVenueListItem({
      id: 104,
      name: 'Musée National',
      managingOffererId: 100,
    }),
    makeVenueListItem({
      id: 105,
      name: 'Galerie Moderne',
      managingOffererId: 100,
    }),
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render', async () => {
    const { container } = renderHub({ venues: venuesBase })

    expect(await axe(container)).toHaveNoViolations()

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: 'À quelle structure souhaitez-vous accéder ?',
      })
    ).toBeInTheDocument()

    expect(screen.getByRole('button', { name: /Venue A/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Venue B/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Venue C/ })).toBeInTheDocument()
  })

  it('should display venue address when location is available', () => {
    const venuesWithLocation = [
      makeVenueListItem({
        id: 101,
        name: 'Venue With Location',
        managingOffererId: 100,
        location: {
          id: 1,
          street: '123 Rue de Test',
          postalCode: '75001',
          city: 'Paris',
          latitude: 48.8566,
          longitude: 2.3522,
          isManualEdition: false,
          isVenueLocation: false,
        },
      }),
    ]

    renderHub({ venues: venuesWithLocation })

    expect(screen.getByText('123 Rue de Test, 75001 Paris')).toBeInTheDocument()
  })

  it('should not display venue address when location is unavailable', () => {
    const venuesWithoutAddress = [
      makeVenueListItem({
        id: 101,
        name: 'Venue Without Location',
        managingOffererId: 100,
        location: undefined,
      }),
    ]

    renderHub({ venues: venuesWithoutAddress })

    expect(
      screen.getByRole('button', { name: 'Venue Without Location' })
    ).toHaveTextContent('Venue Without Location')
  })

  it('should call setSelectedVenueById when clicking on any venue', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 102,
        managingOfferer: {
          id: 100,
          allowedOnAdage: true,
          isValidated: true,
          name: 'Test Offerer',
          siren: '123456789',
        },
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    renderHub({ venues: venuesBase })

    await userEvent.click(screen.getByRole('button', { name: 'Venue B' }))

    await waitFor(() => {
      expect(api.getVenue).toHaveBeenCalledWith(102)
    })
  })

  it('should show spinner after venue selection', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 102,
        managingOfferer: {
          id: 100,
          allowedOnAdage: true,
          isValidated: true,
          name: 'Test Offerer',
          siren: '123456789',
        },
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    renderHub({ venues: venuesBase })

    await userEvent.click(screen.getByRole('button', { name: 'Venue B' }))

    await waitFor(() => {
      expect(
        screen.getByText('Chargement de la structure en cours…')
      ).toBeInTheDocument()
    })
  })

  describe('search functionality', () => {
    it('should not display search input when there are 4 or fewer venues', () => {
      renderHub({ venues: venuesBase })

      expect(
        screen.queryByRole('searchbox', { name: 'Rechercher une structure' })
      ).not.toBeInTheDocument()
    })

    it('should display search input when there are more than 4 venues', () => {
      renderHub({ venues: venuesWithMoreThanFour })

      expect(
        screen.getByRole('searchbox', { name: 'Rechercher une structure' })
      ).toBeInTheDocument()
    })

    it('should filter venues based on search query', async () => {
      renderHub({ venues: venuesWithMoreThanFour })

      const searchInput = screen.getByRole('searchbox', {
        name: 'Rechercher une structure',
      })
      await userEvent.type(searchInput, 'theatre')

      expect(
        screen.getByRole('button', { name: /Théâtre du Soleil/ })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: /Café des Arts/ })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: /Cinéma Lumière/ })
      ).not.toBeInTheDocument()
    })

    it('should filter venues ignoring accents', async () => {
      renderHub({ venues: venuesWithMoreThanFour })

      const searchInput = screen.getByRole('searchbox', {
        name: 'Rechercher une structure',
      })
      await userEvent.type(searchInput, 'cafe')

      expect(
        screen.getByRole('button', { name: /Café des Arts/ })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: /Théâtre du Soleil/ })
      ).not.toBeInTheDocument()
    })

    it('should display no results message when no venues match', async () => {
      renderHub({ venues: venuesWithMoreThanFour })

      const searchInput = screen.getByRole('searchbox', {
        name: 'Rechercher une structure',
      })
      await userEvent.type(searchInput, 'nonexistent')

      expect(
        screen.getByText(
          'Aucune structure ne correspond à votre recherche "nonexistent".'
        )
      ).toBeInTheDocument()
    })

    it('should reset filter when search query is cleared', async () => {
      renderHub({ venues: venuesWithMoreThanFour })

      const searchInput = screen.getByRole('searchbox', {
        name: 'Rechercher une structure',
      })
      await userEvent.type(searchInput, 'theatre')

      expect(
        screen.getByRole('button', { name: /Théâtre du Soleil/ })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: /Café des Arts/ })
      ).not.toBeInTheDocument()

      await userEvent.clear(searchInput)

      expect(
        screen.getByRole('button', { name: /Théâtre du Soleil/ })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /Café des Arts/ })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /Cinéma Lumière/ })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /Musée National/ })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /Galerie Moderne/ })
      ).toBeInTheDocument()
    })

    it('should announce filtered results count for screen readers', async () => {
      renderHub({ venues: venuesWithMoreThanFour })

      const searchInput = screen.getByRole('searchbox', {
        name: 'Rechercher une structure',
      })
      await userEvent.type(searchInput, 'musee')

      expect(screen.getByRole('status')).toHaveTextContent(
        '1 structure trouvée.'
      )
    })

    it('should use plural form in screen reader announcement for multiple results', async () => {
      renderHub({ venues: venuesWithMoreThanFour })

      const searchInput = screen.getByRole('searchbox', {
        name: 'Rechercher une structure',
      })
      await userEvent.type(searchInput, 'a')

      expect(screen.getByRole('status')).toHaveTextContent(
        'structures trouvées'
      )
    })
  })
})
