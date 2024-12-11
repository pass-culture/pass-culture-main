import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
  SharedCurrentUserResponseModel,
  UserRole,
} from 'apiClient/v1'
import {
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import * as useNotification from 'commons/hooks/useNotification'
import { collectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

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
        currentUser: sharedCurrentUserFactory({
          isAdmin: false,
        }),
        selectedOffererId: 1,
      },
    },
    ...options,
  })
}

const categoriesAndSubcategories = {
  categories: [
    { id: 'CINEMA', proLabel: 'Cinéma', isSelectable: true },
    { id: 'JEU', proLabel: 'Jeux', isSelectable: true },
    { id: 'TECHNIQUE', proLabel: 'Technique', isSelectable: false },
  ],
  subcategories: [],
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

vi.mock('commons/utils/date', async () => {
  return {
    ...(await vi.importActual('commons/utils/date')),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('apiClient/api', () => ({
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
  const mockNotifyPending = vi.fn()
  const mockNotifySuccess = vi.fn()
  beforeEach(async () => {
    currentUser = sharedCurrentUserFactory({
      isAdmin: false,
      roles: [UserRole.PRO],
    })
    offersRecap = [collectiveOfferFactory()]

    props = {
      currentPageNumber: 1,
      currentUser,
      isLoading: false,
      offerer: { ...defaultGetOffererResponseModel },
      offers: offersRecap,
      urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      initialSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      redirectWithUrlFilters: vi.fn(),
      venues: proVenuesOptions,
      categories: categoriesAndSubcategories.categories.map(
        ({ id, proLabel }) => ({ value: id, label: proLabel })
      ),
    }

    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
      pending: mockNotifyPending,
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

    expect(screen.getByLabelText(`Sélectionner l'offre "${firstOffer.name}"`)).toBeInTheDocument()
    expect(screen.getByLabelText(`Sélectionner l'offre "${secondOffer.name}"`)).toBeInTheDocument()
  })

  it('should display an unchecked by default checkbox to select all offers when user is not admin', () => {
    const firstOffer = collectiveOfferFactory()
    const secondOffer = collectiveOfferFactory()

    renderOffers({
      ...props,
      currentUser: { ...props.currentUser, isAdmin: false },
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

    screen.getByLabelText(`Sélectionner l'offre "${offersRecap[0].name}"`)
    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({
      ...props,
      offers: offersRecap,
    })

    screen.getByLabelText(`Sélectionner l'offre "${offersRecap[0].name}"`)
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
    offersRecap = Array.from({ length: 501 }, () => collectiveOfferFactory())

    renderOffers({
      ...props,
      offers: offersRecap,
    })

    screen.getByLabelText(`Sélectionner l'offre "${offersRecap[0].name}"`)
    expect(await screen.findByText('500+ offres')).toBeInTheDocument()
  })

  it('should render venue filter with default option selected and given venues as options', () => {
    const expectedSelectOptions = [
      { id: [ALL_VENUES_OPTION.value], value: ALL_VENUES_OPTION.label },
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

    const eventPeriodSelect = screen.queryAllByPlaceholderText('JJ/MM/AAAA')
    expect(eventPeriodSelect).toHaveLength(2)
  })

  it('should not display status filters modal', () => {
    renderOffers(props)

    expect(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    ).toBeInTheDocument()
    expect(screen.queryByText('Afficher les offres')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Tous')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Publiée')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Désactivée')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Épuisée')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Expirée')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Appliquer')).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Validation en attente')
    ).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Refusée')).not.toBeInTheDocument()
  })

  it('should hide status filters when clicking outside the modal', async () => {
    renderOffers(props)
    await userEvent.click(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    )

    await userEvent.click(
      screen.getByRole('heading', {
        name: 'Offres collectives',
        level: 1,
      })
    )

    expect(screen.queryByText('Afficher les offres')).not.toBeInTheDocument()
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
        status: CollectiveOfferStatus.PENDING,
      }),
    ]

    renderOffers({
      ...props,
      offers: offers,
    })

    expect(await screen.findByLabelText('Tout sélectionner')).not.toBeChecked()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<CollectiveOffersScreen {...props} />, {
      user: currentUser,
    })

    const checkbox = screen.getByLabelText(`Sélectionner l'offre "${offersRecap[0].name}"`)
    await userEvent.click(checkbox)

    const actionBar = await screen.findByTestId('actions-bar')
    expect(actionBar).toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(actionBar).not.toBeInTheDocument()
  })

  describe('on click on select all offers checkbox', () => {
    it('should display error message when trying to activate collective offers with booking limit date passed', async () => {
      const offers = [
        collectiveOfferFactory({
          isActive: false,
          hasBookingLimitDatetimesPassed: true,
          stocks: [
            {
              beginningDatetime: String(new Date()),
              hasBookingLimitDatetimePassed: true,
              remainingQuantity: 1,
            },
          ],
        }),
      ]

      renderOffers({
        ...props,
        offers: offers,
      })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
      )
    })

    it('should check all validated offers checkboxes', async () => {
      // Given
      const offers = [
        collectiveOfferFactory({ name: 'offer 1' }),
        collectiveOfferFactory({ name: 'offer 2' }),
        collectiveOfferFactory({
          isActive: false,
          status: CollectiveOfferStatus.REJECTED,
          name: 'offer 3',
        }),
        collectiveOfferFactory({
          status: CollectiveOfferStatus.PENDING,
          name: 'offer 4',
        }),
      ]

      renderOffers({
        ...props,
        offers: offers,
      })

      const firstOfferCheckbox = screen.getByLabelText(`Sélectionner l'offre "${offers[0].name}"`)
      const secondOfferCheckbox = screen.getByLabelText(`Sélectionner l'offre "${offers[1].name}"`)
      const thirdOfferCheckbox = screen.getByLabelText(`Sélectionner l'offre "${offers[2].name}"`)
      const fourthOfferCheckbox = screen.getByLabelText(`Sélectionner l'offre "${offers[3].name}"`)

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
  })

  it('should display the collective offers format', async () => {
    renderOffers({
      ...props,
      offers: [collectiveOfferFactory()],
    })
    expect(await screen.findByRole('combobox', { name: 'Format' }))
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

  it('should display a new column "Date de l’évènement" if FF is enabled', async () => {
    const featureOverrides = {
      features: ['ENABLE_COLLECTIVE_OFFERS_EXPIRATION'],
    }

    renderOffers(
      {
        ...props,
        offers: [collectiveOfferFactory()],
      },
      featureOverrides
    )

    expect(await screen.findByText('Date de l’évènement'))
  })

  it('should filter new column "Date de l’évènement"', async () => {
    const featureOverrides = {
      features: ['ENABLE_COLLECTIVE_OFFERS_EXPIRATION'],
    }

    renderOffers(
      {
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
      },
      featureOverrides
    )

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
      screen.queryByRole('combobox', { name: 'Type de l’offre' })
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
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    )

    expect(
      screen.queryByRole('option', { name: 'Masquée sur ADAGE' })
    ).not.toBeInTheDocument()
  })

  it('should show the reimbursed status option if the ENABLE_COLLECTIVE_NEW_STATUSES FF is active', async () => {
    renderOffers(
      {
        ...props,
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    await userEvent.click(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    )

    expect(
      screen.getByRole('option', { name: 'Remboursée' })
    ).toBeInTheDocument()
  })

  it('should display "Structure" instead of "Lieu" of the WIP_ENABLE_OFFER_ADDRESS FF is active', () => {
    renderOffers(
      {
        ...props,
      },
      { features: ['WIP_ENABLE_OFFER_ADDRESS'] }
    )

    // In filters
    expect(
      screen.getByRole('combobox', { name: 'Structure' })
    ).toBeInTheDocument()

    // In table results
    expect(
      screen.getByRole('columnheader', { name: 'Structure' })
    ).toBeInTheDocument()
  })

  it('should show the cancelled status option if the ENABLE_COLLECTIVE_NEW_STATUSES FF is active', async () => {
    renderOffers(
      {
        ...props,
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    await userEvent.click(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    )

    expect(screen.getByRole('option', { name: 'Annulée' })).toBeInTheDocument()
  })

  it('should not show the cancelled status option if the ENABLE_COLLECTIVE_NEW_STATUSES FF is inactive', async () => {
    renderOffers({
      ...props,
    })

    await userEvent.click(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    )

    expect(
      screen.queryByRole('option', { name: 'Annulée' })
    ).not.toBeInTheDocument()
  })
})
