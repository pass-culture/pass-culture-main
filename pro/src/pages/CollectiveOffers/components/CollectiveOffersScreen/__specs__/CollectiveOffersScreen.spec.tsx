import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import {
  CollectiveOfferResponseModel,
  SharedCurrentUserResponseModel,
  UserRole,
} from '@/apiClient//v1'
import {
  ALL_OFFERERS_OPTION,
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import * as useNotification from '@/commons/hooks/useNotification'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  CollectiveOffersScreen,
  CollectiveOffersScreenProps,
} from '../CollectiveOffersScreen'

const renderOffers = (
  props: CollectiveOffersScreenProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOffersScreen {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
      },
      offerer: currentOffererFactory(),
    },
    ...options,
  })
}

const proVenues = [
  {
    id: 'JI',
    name: 'Ma venue',
    offererName: 'Mon offerer',
    isVirtual: false,
  },
  {
    id: 'JQ',
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  },
]
const proVenuesOptions = [
  { value: 'JI', label: 'Ma venue' },
  { value: 'JQ', label: 'Mon offerer - Offre numérique' },
]

vi.mock('@/commons/utils/date', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/date')),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('@/apiClient//api', () => ({
  api: {
    listOfferersNames: vi.fn().mockReturnValue({}),
    deleteDraftOffers: vi.fn(),
  },
}))

describe('CollectiveOffersScreen', () => {
  let props: CollectiveOffersScreenProps
  let currentUser: SharedCurrentUserResponseModel
  let offersRecap: CollectiveOfferResponseModel[]

  const mockNotifyError = vi.fn()
  const mockNotifySuccess = vi.fn()
  beforeEach(async () => {
    currentUser = sharedCurrentUserFactory({
      roles: [UserRole.PRO],
    })
    offersRecap = [collectiveOfferFactory()]

    props = {
      currentPageNumber: 1,
      isLoading: false,
      offerer: { ...defaultGetOffererResponseModel },
      offers: offersRecap,
      urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      initialSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      redirectWithUrlFilters: vi.fn(),
      venues: proVenuesOptions,
    }

    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
      success: mockNotifySuccess,
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

  it('should render venue filter with default option selected and given venues as options', () => {
    const expectedSelectOptions = [
      {
        id: [ALL_VENUES_OPTION.value],
        value: ALL_OFFERERS_OPTION.label,
      },
      { id: [proVenues[0].id], value: proVenues[0].name },
      {
        id: [proVenues[1].id],
        value: `${proVenues[1].offererName} - Offre numérique`,
      },
    ]

    renderOffers(props)

    const defaultOption = screen.getByDisplayValue(
      expectedSelectOptions[0].value
    )
    expect(defaultOption).toBeInTheDocument()

    const firstVenueOption = screen.getByRole('option', {
      name: expectedSelectOptions[1].value,
    })
    expect(firstVenueOption).toBeInTheDocument()

    const secondVenueOption = screen.getByRole('option', {
      name: expectedSelectOptions[2].value,
    })
    expect(secondVenueOption).toBeInTheDocument()
  })

  it('should render venue filter with given venue selected', () => {
    const expectedSelectOptions = [
      { id: [proVenues[0].id], value: proVenues[0].name },
    ]
    const filters = {
      ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      venueId: proVenues[0].id,
    }

    renderOffers({ ...props, initialSearchFilters: filters })

    const venueSelect = screen.getByDisplayValue(expectedSelectOptions[0].value)
    expect(venueSelect).toBeInTheDocument()
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
    expect(await screen.findByLabelText('En pause')).toBeInTheDocument()
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
    const offers = [
      collectiveOfferFactory({
        isActive: false,
      }),
    ]

    renderOffers({
      ...props,
      offers,
    })

    expect(await screen.findByLabelText('Tout sélectionner')).not.toBeChecked()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<CollectiveOffersScreen {...props} />, {
      user: currentUser,
    })

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

  it('should filter new column "Date de l’évènement"', async () => {
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
      screen.getByRole('button', {
        name: 'Trier par ordre croissant',
      })
    )

    const newFirstOfferEventDate =
      screen.getAllByTestId('offer-event-date')[0].textContent

    expect(newFirstOfferEventDate).toEqual('30/06/2024')
  })

  it('should not display the offer type filter if the WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE FF is active', () => {
    renderOffers(
      {
        ...props,
      },
      { features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'] }
    )
    expect(
      screen.queryByRole('button', { name: 'Type de l’offre' })
    ).not.toBeInTheDocument()
  })

  it('should not show the inactive status option if the WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE FF is active', async () => {
    renderOffers(
      {
        ...props,
      },
      { features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'] }
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Statut',
      })
    )

    expect(
      screen.queryByRole('option', { name: 'En pause' })
    ).not.toBeInTheDocument()
  })

  it('should display "Structure"', () => {
    renderOffers({
      ...props,
    })

    // In filters
    expect(
      screen.getByRole('combobox', { name: 'Structure' })
    ).toBeInTheDocument()

    // In table results
    expect(
      screen.getByRole('columnheader', { name: 'Structure' })
    ).toBeInTheDocument()
  })
})
