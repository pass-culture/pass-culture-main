import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  UserRole,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  CollectiveOffersScreen,
  type CollectiveOffersScreenProps,
} from './CollectiveOffersScreen'

const renderOffers = (
  props: CollectiveOffersScreenProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOffersScreen {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory({
          roles: [UserRole.PRO],
        }),
      },
      offerer: currentOffererFactory(),
    },
    ...options,
  })
}

vi.mock('@/commons/utils/date', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/date')),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn().mockReturnValue({}),
    deleteDraftOffers: vi.fn(),
    getVenues: vi.fn(),
  },
}))

describe('CollectiveOffersScreen', () => {
  let props: CollectiveOffersScreenProps
  let offersRecap: CollectiveOfferResponseModel[]

  const snackBarError = vi.fn()
  const snackBarSuccess = vi.fn()
  beforeEach(async () => {
    offersRecap = [collectiveOfferFactory()]

    props = {
      currentPageNumber: 1,
      isLoading: false,
      offererId: '1',
      offers: offersRecap,
      urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      initialSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      redirectWithUrlFilters: vi.fn(),
    }

    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
      success: snackBarSuccess,
    }))
  })

  it('should render as much offers as returned by the api', () => {
    const firstOffer = collectiveOfferFactory()
    const secondOffer = collectiveOfferFactory()

    renderOffers({
      ...props,
      offers: [firstOffer, secondOffer],
    })

    expect(
      screen.getByRole('checkbox', { name: firstOffer.name })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: secondOffer.name })
    ).toBeInTheDocument()
  })

  it('should display an unchecked by default checkbox to select all offers', () => {
    const firstOffer = collectiveOfferFactory()
    const secondOffer = collectiveOfferFactory()

    renderOffers({
      ...props,
      offers: [firstOffer, secondOffer],
    })

    const selectAllOffersCheckbox = screen.queryByLabelText('Tout sélectionner')
    expect(selectAllOffersCheckbox).toBeInTheDocument()
    expect(selectAllOffersCheckbox).not.toBeChecked()
    expect(selectAllOffersCheckbox).not.toBeDisabled()
  })

  it('should display total number of offers in plural if multiple offers', () => {
    renderOffers({
      ...props,
      offers: [...offersRecap, collectiveOfferFactory()],
    })

    expect(
      screen.getByRole('checkbox', { name: offersRecap[0].name })
    ).toBeInTheDocument()
    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({
      ...props,
      offers: offersRecap,
    })

    expect(
      screen.getByRole('checkbox', { name: offersRecap[0].name })
    ).toBeInTheDocument()
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 100+ for total number of offers if more than 500 offers are fetched', async () => {
    offersRecap = Array.from({ length: 501 }, () => collectiveOfferFactory())

    renderOffers({
      ...props,
      offers: offersRecap,
    })

    expect(
      screen.getByRole('checkbox', { name: offersRecap[0].name })
    ).toBeInTheDocument()
    expect(await screen.findByText('100+ offres')).toBeInTheDocument()
  })

  it('should display event period filter with no default option', () => {
    renderOffers(props)

    const eventPeriodSelect = screen.queryAllByLabelText(/période/)
    expect(eventPeriodSelect).toHaveLength(2)
  })

  it('should display status checkboxes on press status filter', async () => {
    renderOffers(props)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Statut',
      })
    )

    expect(
      await screen.findByLabelText('Publiée sur ADAGE')
    ).toBeInTheDocument()
    expect(await screen.findByLabelText('Expirée')).toBeInTheDocument()
    expect(await screen.findByLabelText('En instruction')).toBeInTheDocument()
    expect(await screen.findByLabelText('Non conforme')).toBeInTheDocument()
    expect(await screen.findByLabelText('Archivée')).toBeInTheDocument()
    expect(await screen.findByLabelText('Réservée')).toBeInTheDocument()
    expect(await screen.findByLabelText('Préréservée')).toBeInTheDocument()
    expect(await screen.findByLabelText('Terminée')).toBeInTheDocument()
    expect(await screen.findByLabelText('Brouillon')).toBeInTheDocument()
    expect(await screen.findByLabelText('Remboursée')).toBeInTheDocument()
    expect(await screen.findByLabelText('Annulée')).toBeInTheDocument()
  })

  it('should indicate that user has no offers yet', () => {
    renderOffers({ ...props, offers: [] })

    const noOffersText = screen.getByText('Vous n’avez pas encore créé d’offre')
    expect(noOffersText).toBeInTheDocument()
  })

  it('should not have "Tout Sélectionner" checked when there is no offer to be checked', async () => {
    const offers = [collectiveOfferFactory()]

    renderOffers({
      ...props,
      offers,
    })

    expect(await screen.findByLabelText('Tout sélectionner')).not.toBeChecked()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderOffers(props)

    const checkbox = screen.getByRole('checkbox', { name: offersRecap[0].name })
    await userEvent.click(checkbox)

    const actionBar = await screen.findByTestId('actions-bar')
    expect(actionBar).toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(actionBar).not.toBeInTheDocument()
  })

  it('should check all validated offers checkboxes', async () => {
    const offers = [
      collectiveOfferFactory({ name: 'offer 1' }),
      collectiveOfferFactory({ name: 'offer 2' }),
      collectiveOfferFactory({ name: 'offer 3' }),
      collectiveOfferFactory({ name: 'offer 4' }),
    ]

    renderOffers({
      ...props,
      offers,
    })

    const firstOfferCheckbox = screen.getByRole('checkbox', {
      name: offers[0].name,
    })
    const secondOfferCheckbox = screen.getByRole('checkbox', {
      name: offers[1].name,
    })
    const thirdOfferCheckbox = screen.getByRole('checkbox', {
      name: offers[2].name,
    })
    const fourthOfferCheckbox = screen.getByRole('checkbox', {
      name: offers[3].name,
    })

    await userEvent.click(screen.getByLabelText('Tout sélectionner'))

    expect(firstOfferCheckbox).toBeChecked()
    expect(secondOfferCheckbox).toBeChecked()
    expect(thirdOfferCheckbox).toBeChecked()
    expect(fourthOfferCheckbox).toBeChecked()

    await userEvent.click(screen.getByLabelText('Tout désélectionner'))

    expect(firstOfferCheckbox).not.toBeChecked()
    expect(secondOfferCheckbox).not.toBeChecked()
    expect(thirdOfferCheckbox).not.toBeChecked()
    expect(fourthOfferCheckbox).not.toBeChecked()
  })

  it('should filter on the format', async () => {
    renderOffers({
      ...props,
      offers: [collectiveOfferFactory()],
    })

    const formatSelect = screen.getByRole('combobox', { name: 'Format' })

    await userEvent.selectOptions(
      formatSelect,
      screen.getByRole('option', { name: 'Concert' })
    )

    const searchButton = screen.getByText('Rechercher')

    await userEvent.click(searchButton)

    expect(props.redirectWithUrlFilters).toHaveBeenCalledWith(
      expect.objectContaining({
        format: 'Concert',
      })
    )
  })

  it('should filter and sort column "Dates"', async () => {
    renderOffers({
      ...props,
      offers: [
        collectiveOfferFactory({
          dates: {
            start: '2024-07-31T09:11:00Z',
            end: '2024-07-31T09:11:00Z',
          },
        }),
        collectiveOfferFactory({
          dates: {
            start: '2024-06-30T09:11:00Z',
            end: '2024-06-30T09:11:00Z',
          },
        }),
      ],
    })
    const firstOfferEventDate =
      screen.getAllByTestId('offer-event-date')[0].textContent

    expect(firstOfferEventDate).toEqual('31/07/2024')

    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre croissant' })
    )

    const offerEventDates = await screen.findAllByTestId('offer-event-date')

    const newFirstOfferEventDate = offerEventDates[0].textContent

    expect(newFirstOfferEventDate).toEqual('30/06/2024')
  })

  it('should render download button', () => {
    renderOffers(props)
    const downloadButton = screen.getByRole('button', {
      name: 'Télécharger',
    })
    expect(downloadButton).toBeInTheDocument()
  })

  describe('ExpirationCell', () => {
    it('should render expiration row when offer is PREBOOKED and has a booking limit', () => {
      const offer = collectiveOfferFactory({
        stock: {
          bookingLimitDatetime: '2024-07-31T09:11:00Z',
        },
        displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      })

      renderOffers({
        ...props,
        offers: [offer],
      })

      expect(
        screen.getByText(
          'En attente de réservation par le chef d’établissement'
        )
      ).toBeInTheDocument()
    })

    it('should render expiration row when offer is PUBLISHED and has a booking limit', () => {
      const offer = collectiveOfferFactory({
        stock: {
          bookingLimitDatetime: '2024-07-31T09:11:00Z',
        },
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      })

      renderOffers({
        ...props,
        offers: [offer],
      })

      expect(
        screen.getByText('En attente de préréservation par l’enseignant')
      ).toBeInTheDocument()
    })

    it('should not render expiration row when offer is not PREBOOKED or PUBLISHED', () => {
      const offer = collectiveOfferFactory({
        stock: {
          bookingLimitDatetime: '2024-07-31T09:11:00Z',
        },
        displayedStatus: CollectiveOfferDisplayedStatus.BOOKED,
      })

      renderOffers({
        ...props,
        offers: [offer],
      })

      expect(screen.queryByText('En attente de')).not.toBeInTheDocument()
    })

    it('should not render expiration row when offer has no booking limit', () => {
      const offer = collectiveOfferFactory({
        stock: {
          bookingLimitDatetime: null,
        },
        displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      })

      renderOffers({
        ...props,
        offers: [offer],
      })

      expect(screen.queryByText('En attente de')).not.toBeInTheDocument()
    })
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    const optionsBase: RenderWithProvidersOptions = {
      features: ['WIP_SWITCH_VENUE'],
    }

    it('should not display the filters button as active when no filters are applied', () => {
      renderOffers(props, optionsBase)

      const filtersButton = screen.getByRole('button', { name: /Filtrer/ })
      expect(filtersButton).toBeInTheDocument()
      expect(
        within(filtersButton).queryByText('actifs')
      ).not.toBeInTheDocument()
    })
  })
})
