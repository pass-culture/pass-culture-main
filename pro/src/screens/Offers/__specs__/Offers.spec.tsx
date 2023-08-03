import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { UserRole } from 'apiClient/v1'
import {
  ALL_CATEGORIES,
  ALL_COLLECTIVE_OFFER_TYPE,
  ALL_CREATION_MODES,
  ALL_EVENT_PERIODS,
  ALL_OFFERERS,
  ALL_OFFERS,
  ALL_STATUS,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import * as useNotification from 'hooks/useNotification'
import { offererFactory } from 'utils/apiFactories'
import { individualOfferOffererFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Offers, { OffersProps } from '../Offers'
import { individualOfferFactory } from '../utils/individualOffersFactories'

const renderOffers = (props: OffersProps, storeOverrides: any) => {
  renderWithProviders(<Offers {...props} />, { storeOverrides })
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

vi.mock('utils/date', async () => {
  return {
    ...((await vi.importActual('utils/date')) ?? {}),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn().mockReturnValue({}),
    patchAllCollectiveOffersActiveStatus: vi.fn(),
  },
}))

describe('screen Offers', () => {
  let props: OffersProps
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
    roles: Array<UserRole>
  }
  let store: any
  let offersRecap: Offer[]

  const mockNotifyError = vi.fn()
  const mockNotifyPending = vi.fn()
  beforeEach(() => {
    currentUser = {
      id: 'EY',
      isAdmin: false,
      name: 'Current User',
      roles: [UserRole.PRO],
    }
    store = {
      user: {
        initialized: true,
        currentUser,
      },
      offers: {
        searchFilters: DEFAULT_SEARCH_FILTERS,
      },
    }
    offersRecap = [individualOfferFactory()]

    props = {
      currentPageNumber: 1,
      currentUser,
      isLoading: false,
      loadAndUpdateOffers: vi.fn().mockResolvedValue(offersRecap),
      offerer: offererFactory(),
      offers: offersRecap,
      setIsLoading: vi.fn(),
      setOfferer: vi.fn(),
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
      separateIndividualAndCollectiveOffers: false,
      initialSearchFilters: DEFAULT_SEARCH_FILTERS,
      audience: Audience.INDIVIDUAL,
      redirectWithUrlFilters: vi.fn(),
      venues: proVenuesOptions,
      categories: categoriesAndSubcategories.categories.map(
        ({ id, proLabel }) => ({ value: id, label: proLabel })
      ),
    } as OffersProps
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...vi.importActual('hooks/useNotification'),
      error: mockNotifyError,
      pending: mockNotifyPending,
    }))
  })

  it('should load offers from API with defaults props', () => {
    renderOffers(props, store)

    expect(props.loadAndUpdateOffers).toHaveBeenCalledWith({
      nameOrIsbn: ALL_OFFERS,
      venueId: ALL_VENUES,
      categoryId: ALL_CATEGORIES,
      offererId: ALL_OFFERERS,
      status: ALL_STATUS,
      creationMode: ALL_CREATION_MODES,
      page: DEFAULT_PAGE,
      periodBeginningDate: ALL_EVENT_PERIODS,
      periodEndingDate: ALL_EVENT_PERIODS,
      collectiveOfferType: ALL_COLLECTIVE_OFFER_TYPE,
    })
  })

  it('should display column titles when offers are returned', async () => {
    renderOffers(props, store)

    expect(screen.getByText('Lieu', { selector: 'th' })).toBeInTheDocument()
    expect(screen.getByText('Stocks', { selector: 'th' })).toBeInTheDocument()
  })

  it('should render as much offers as returned by the api', async () => {
    const firstOffer = individualOfferFactory()
    const secondOffer = individualOfferFactory()

    renderOffers(
      {
        ...props,
        offers: [firstOffer, secondOffer],
      },
      store
    )

    const firstOfferLine = screen.getByText(firstOffer.name)
    expect(firstOfferLine).toBeInTheDocument()
    expect(screen.getByText(secondOffer.name)).toBeInTheDocument()
  })

  it('should display an unchecked by default checkbox to select all offers when user is not admin', async () => {
    const firstOffer = individualOfferFactory()
    const secondOffer = individualOfferFactory()

    renderOffers(
      {
        ...props,
        currentUser: { ...props.currentUser, isAdmin: false },
        offers: [firstOffer, secondOffer],
      },
      store
    )

    screen.getByText(firstOffer.name)
    const selectAllOffersCheckbox = screen.queryByLabelText('Tout sélectionner')
    expect(selectAllOffersCheckbox).toBeInTheDocument()
    expect(selectAllOffersCheckbox).not.toBeChecked()
    expect(selectAllOffersCheckbox).not.toBeDisabled()
  })

  it('should display total number of offers in plural if multiple offers', async () => {
    renderOffers(
      {
        ...props,
        offers: [...offersRecap, individualOfferFactory()],
      },
      store
    )

    screen.getByText(offersRecap[0].name)
    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({ ...props, offers: offersRecap }, store)

    screen.getByText(offersRecap[0].name)
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
    offersRecap = Array.from({ length: 501 }, () => individualOfferFactory())

    renderOffers({ ...props, offers: offersRecap }, store)

    screen.getByText(offersRecap[0].name)
    expect(await screen.findByText('500+ offres')).toBeInTheDocument()
  })

  it('should render venue filter with default option selected and given venues as options', async () => {
    const expectedSelectOptions = [
      { id: [ALL_VENUES_OPTION.value], value: ALL_VENUES_OPTION.label },
      { id: [proVenues[0].id], value: proVenues[0].name },
      {
        id: [proVenues[1].id],
        value: `${proVenues[1].offererName} - Offre numérique`,
      },
    ]

    renderOffers(props, store)

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

  it('should render venue filter with given venue selected', async () => {
    const expectedSelectOptions = [
      { id: [proVenues[0].id], value: proVenues[0].name },
    ]
    const filters = { ...DEFAULT_SEARCH_FILTERS, venueId: proVenues[0].id }

    renderOffers({ ...props, initialSearchFilters: filters }, store)

    const venueSelect = screen.getByDisplayValue(expectedSelectOptions[0].value)
    expect(venueSelect).toBeInTheDocument()
  })

  it('should render creation mode filter with default option selected', async () => {
    renderOffers(props, store)

    expect(screen.getByDisplayValue('Tous')).toBeInTheDocument()
  })

  it('should render creation mode filter with given creation mode selected', async () => {
    renderOffers(
      {
        ...props,
        initialSearchFilters: {
          ...DEFAULT_SEARCH_FILTERS,
          creationMode: 'imported',
        },
      },
      store
    )

    expect(screen.getByDisplayValue('Synchronisé')).toBeInTheDocument()
  })

  it('should allow user to select manual creation mode filter', async () => {
    renderOffers(props, store)
    const creationModeSelect = screen.getByLabelText('Mode de création')

    await userEvent.selectOptions(creationModeSelect, 'Manuel')

    expect(screen.getByDisplayValue('Manuel')).toBeInTheDocument()
  })

  it('should allow user to select imported creation mode filter', async () => {
    renderOffers(props, store)
    const creationModeSelect = screen.getByDisplayValue('Tous')

    await userEvent.selectOptions(creationModeSelect, 'imported')

    expect(screen.getByDisplayValue('Synchronisé')).toBeInTheDocument()
  })

  it('should display event period filter with no default option', async () => {
    renderOffers(props, store)

    const eventPeriodSelect = screen.queryAllByPlaceholderText('JJ/MM/AAAA')
    expect(eventPeriodSelect).toHaveLength(2)
  })

  it('should not display status filters modal', async () => {
    renderOffers(props, store)

    expect(screen.getByText('Statut')).toBeInTheDocument()
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

  it('should display status filters with "Toutes" as default value when clicking on "Statut" filter icon', async () => {
    renderOffers(props, store)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Statut Afficher ou masquer le filtre par statut',
      })
    )

    expect(screen.queryByText('Afficher les offres')).toBeInTheDocument()
    expect(screen.getByLabelText('Toutes')).toBeChecked()
    expect(screen.getByLabelText('Publiée')).not.toBeChecked()
    expect(screen.getByLabelText('Désactivée')).not.toBeChecked()
    expect(screen.getByLabelText('Épuisée')).not.toBeChecked()
    expect(screen.getByLabelText('Expirée')).not.toBeChecked()
    expect(screen.getByLabelText('Brouillon')).not.toBeChecked()
    expect(screen.getByLabelText('Validation en attente')).not.toBeChecked()
    expect(screen.getByLabelText('Refusée')).not.toBeChecked()
    expect(
      screen.queryByText('Appliquer', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should hide status filters when clicking outside the modal', async () => {
    renderOffers(props, store)
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Statut Afficher ou masquer le filtre par statut',
      })
    )

    await userEvent.click(
      screen.getByRole('heading', {
        name: 'Offres',
        level: 1,
      })
    )

    expect(screen.queryByText('Afficher les offres')).not.toBeInTheDocument()
  })

  it('should indicate that user has no offers yet', async () => {
    renderOffers({ ...props, offers: [] }, store)

    const noOffersText = screen.getByText('Vous n’avez pas encore créé d’offre')
    expect(noOffersText).toBeInTheDocument()
  })

  describe('when user is admin', () => {
    beforeEach(() => {
      props.currentUser.isAdmin = true
    })

    describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
      it('should disable status filters when no venue nor offerer filter is selected', async () => {
        renderOffers(props, store)

        expect(
          screen.getByRole('button', {
            name: 'Statut Afficher ou masquer le filtre par statut',
          })
        ).toBeDisabled()
      })

      it('should disable status filters when no venue filter is selected, even if one venue filter is currently applied', async () => {
        renderOffers(
          {
            ...props,
            initialSearchFilters: {
              ...DEFAULT_SEARCH_FILTERS,
              venueId: 'JI',
            },
          },
          store
        )

        await userEvent.selectOptions(
          screen.getByDisplayValue('Ma venue'),
          'all'
        )

        expect(
          screen.getByRole('button', {
            name: 'Statut Afficher ou masquer le filtre par statut',
          })
        ).toBeDisabled()
      })

      it('should enable status filters when venue is selected but filter is not applied', async () => {
        renderOffers(props, store)
        const venueOptionToSelect = screen.getByRole('option', {
          name: proVenues[0].name,
        })

        await userEvent.selectOptions(
          screen.getByLabelText('Lieu'),
          venueOptionToSelect
        )

        expect(
          screen.getByRole('button', {
            name: 'Statut Afficher ou masquer le filtre par statut',
          })
        ).not.toBeDisabled()
      })
    })

    describe('select all offers checkbox', () => {
      it('should disable select all checkbox when no venue nor offerer filter is applied', async () => {
        renderOffers(props, store)

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).toBeDisabled()
      })

      it('should not disable select all checkbox when no venue filter is selected but one is currently applied', async () => {
        renderOffers(
          {
            ...props,
            initialSearchFilters: {
              ...DEFAULT_SEARCH_FILTERS,
              venueId: 'JI',
            },
          },
          {
            user: {
              initialized: true,
              currentUser,
            },
            offers: {
              searchFilters: { ...DEFAULT_SEARCH_FILTERS, venueId: 'JI' },
            },
          }
        )

        await userEvent.selectOptions(
          screen.getByDisplayValue('Ma venue'),
          'all'
        )

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).not.toBeDisabled()
      })

      it('should disable select all checkbox when venue filter is selected but not applied', async () => {
        renderOffers(props, store)

        await userEvent.selectOptions(
          screen.getByDisplayValue('Tous les lieux'),
          'JI'
        )

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).toBeDisabled()
      })

      it('should enable select all checkbox when venue filter is applied', async () => {
        renderOffers(
          {
            ...props,
            initialSearchFilters: {
              ...DEFAULT_SEARCH_FILTERS,
              venueId: 'IJ',
            },
          },
          {
            user: {
              initialized: true,
              currentUser,
            },
            offers: {
              searchFilters: { ...DEFAULT_SEARCH_FILTERS, venueId: 'IJ' },
            },
          }
        )

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).not.toBeDisabled()
      })

      it('should enable select all checkbox when offerer filter is applied', async () => {
        renderOffers(
          {
            ...props,
            initialSearchFilters: {
              ...DEFAULT_SEARCH_FILTERS,
              offererId: 'A4',
            },
          },
          {
            user: {
              initialized: true,
              currentUser,
            },
            offers: {
              searchFilters: { ...DEFAULT_SEARCH_FILTERS, offererId: 'A4' },
            },
          }
        )

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).not.toBeDisabled()
      })
    })
  })

  it('should disabled checkbox when offer is rejected or pending for validation', async () => {
    props.currentUser.isAdmin = false
    const offers = [
      individualOfferFactory({
        isActive: false,
        status: 'REJECTED',
      }),
      individualOfferFactory({
        isActive: true,
        status: 'PENDING',
      }),
      individualOfferFactory({
        isActive: true,
        status: 'ACTIVE',
      }),
    ]

    renderOffers({ ...props, offers }, store)

    screen.getByText(offers[0].name)
    expect(screen.queryByTestId(`select-offer-${offers[0].id}`)).toBeDisabled()
    expect(screen.queryByTestId(`select-offer-${offers[1].id}`)).toBeDisabled()
    expect(screen.queryByTestId(`select-offer-${offers[2].id}`)).toBeEnabled()
  })

  it('should load offers on click on search button with default filters when no changes where made', async () => {
    renderOffers(props, store)

    await userEvent.click(screen.getByText('Lancer la recherche'))

    expect(props.loadAndUpdateOffers).toHaveBeenCalledWith({
      nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
      venueId: DEFAULT_SEARCH_FILTERS.venueId,
      categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
      status: DEFAULT_SEARCH_FILTERS.status,
      creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
      page: DEFAULT_SEARCH_FILTERS.page,
      periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
      periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      collectiveOfferType: ALL_COLLECTIVE_OFFER_TYPE,
    })
  })

  it('should not display the button to create an offer when user is an admin', async () => {
    props.currentUser.isAdmin = true

    await renderOffers(props, store)

    expect(screen.queryByText('Créer une offre')).toBeNull()
  })

  it('should display the button to create an offer when user is not an admin', async () => {
    const individualOffererNames = individualOfferOffererFactory()
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [individualOffererNames],
    })

    props.currentUser.isAdmin = false

    await renderOffers(props, store)

    expect(
      await screen.findByRole('link', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })

  it('should not display button to create an offer when user is not yet validated', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
    })
    await renderOffers(props, store)

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })

    expect(
      screen.queryByRole('link', { name: /Créer une offre/ })
    ).not.toBeInTheDocument()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<Offers {...props} />, { storeOverrides: store })

    const checkbox = screen.getByTestId(`select-offer-${offersRecap[0].id}`)
    await userEvent.click(checkbox)

    const actionBar = await screen.findByTestId('actions-bar')
    expect(actionBar).toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(actionBar).not.toBeInTheDocument()
  })

  describe('on click on select all offers checkbox', () => {
    it('should display "Tout désélectionner" when initial label was "Tout sélectionner"', async () => {
      renderOffers(props, store)

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))

      expect(screen.queryByLabelText('Tout désélectionner')).toBeInTheDocument()
    })

    it('should display display error message when trying to activate draft offers', async () => {
      const offers = [
        individualOfferFactory({
          isActive: false,
          status: 'DRAFT',
        }),
      ]

      renderOffers({ ...props, offers }, store)

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des brouillons depuis cette liste'
      )
    })

    it('should display display error message when trying to activate collective offers with booking limit date passed', async () => {
      const offers = [
        individualOfferFactory({
          isActive: false,
          hasBookingLimitDatePassed: true,
        }),
      ]

      renderOffers({ ...props, audience: Audience.COLLECTIVE, offers }, store)

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
      )
    })

    it('should display success message activate inactive collective offer', async () => {
      const offers = [
        individualOfferFactory({
          isActive: false,
          hasBookingLimitDatetimesPassed: false,
        }),
      ]

      renderOffers({ ...props, audience: Audience.COLLECTIVE, offers }, store)

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(api.patchAllCollectiveOffersActiveStatus).toHaveBeenCalledTimes(1)
    })

    it('should check all validated offers checkboxes', async () => {
      // Given
      const offers = [
        individualOfferFactory(),
        individualOfferFactory({
          isFullyBooked: true,
        }),
        individualOfferFactory({
          isActive: false,
          status: 'REJECTED',
        }),
        individualOfferFactory({
          status: 'PENDING',
        }),
      ]

      renderOffers({ ...props, offers }, store)

      const firstOfferCheckbox = screen.getByTestId(
        `select-offer-${offers[0].id}`
      )
      const secondOfferCheckbox = screen.getByTestId(
        `select-offer-${offers[1].id}`
      )
      const thirdOfferCheckbox = screen.getByTestId(
        `select-offer-${offers[2].id}`
      )
      const fourthOfferCheckbox = screen.getByTestId(
        `select-offer-${offers[3].id}`
      )

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))

      expect(firstOfferCheckbox).toBeChecked()
      expect(secondOfferCheckbox).toBeChecked()
      expect(thirdOfferCheckbox).not.toBeChecked()
      expect(fourthOfferCheckbox).not.toBeChecked()

      await userEvent.click(screen.getByLabelText('Tout désélectionner'))

      expect(firstOfferCheckbox).not.toBeChecked()
      expect(secondOfferCheckbox).not.toBeChecked()
      expect(thirdOfferCheckbox).not.toBeChecked()
      expect(fourthOfferCheckbox).not.toBeChecked()
    })
  })
})
