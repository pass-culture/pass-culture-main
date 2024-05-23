import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  ListOffersOfferResponseModel,
  OfferStatus,
  SharedCurrentUserResponseModel,
  UserRole,
} from 'apiClient/v1'
import {
  ALL_VENUES_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Audience } from 'core/shared/types'
import * as useNotification from 'hooks/useNotification'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  getOfferManagingOffererFactory,
  listOffersOfferFactory,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Offers, OffersProps } from '../Offers'

const renderOffers = (
  props: OffersProps,
  options?: RenderWithProvidersOptions,
  hasNewNav: boolean = false
) => {
  renderWithProviders(<Offers {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory({
          isAdmin: false,
          navState: {
            newNavDate: hasNewNav ? '2021-01-01' : null,
          },
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

vi.mock('utils/date', async () => {
  return {
    ...(await vi.importActual('utils/date')),
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
  let currentUser: SharedCurrentUserResponseModel
  let offersRecap: ListOffersOfferResponseModel[]

  const mockNotifyError = vi.fn()
  const mockNotifyPending = vi.fn()
  beforeEach(async () => {
    currentUser = sharedCurrentUserFactory({
      isAdmin: false,
      roles: [UserRole.PRO],
    })
    offersRecap = [listOffersOfferFactory()]

    props = {
      currentPageNumber: 1,
      currentUser,
      isLoading: false,
      offerer: { ...defaultGetOffererResponseModel },
      offers: offersRecap,
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
      initialSearchFilters: DEFAULT_SEARCH_FILTERS,
      audience: Audience.INDIVIDUAL,
      redirectWithUrlFilters: vi.fn(),
      venues: proVenuesOptions,
      categories: categoriesAndSubcategories.categories.map(
        ({ id, proLabel }) => ({ value: id, label: proLabel })
      ),
    }

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
      pending: mockNotifyPending,
    }))
  })

  it('should display column titles when offers are returned', () => {
    renderOffers(props)

    expect(screen.getByText('Lieu', { selector: 'th' })).toBeInTheDocument()
    expect(screen.getByText('Stocks', { selector: 'th' })).toBeInTheDocument()
  })

  it('should render as much offers as returned by the api', () => {
    const firstOffer = listOffersOfferFactory()
    const secondOffer = listOffersOfferFactory()

    renderOffers({
      ...props,
      offers: [firstOffer, secondOffer],
    })

    expect(screen.getByLabelText(firstOffer.name)).toBeInTheDocument()
    expect(screen.getByLabelText(secondOffer.name)).toBeInTheDocument()
  })

  it('should display an unchecked by default checkbox to select all offers when user is not admin', () => {
    const firstOffer = listOffersOfferFactory()
    const secondOffer = listOffersOfferFactory()

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
      offers: [...offersRecap, listOffersOfferFactory()],
    })

    screen.getByLabelText(offersRecap[0].name)
    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({ ...props, offers: offersRecap })

    screen.getByLabelText(offersRecap[0].name)
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
    offersRecap = Array.from({ length: 501 }, () => listOffersOfferFactory())

    renderOffers({ ...props, offers: offersRecap })

    screen.getByLabelText(offersRecap[0].name)
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
    const filters = { ...DEFAULT_SEARCH_FILTERS, venueId: proVenues[0].id }

    renderOffers({ ...props, initialSearchFilters: filters })

    const venueSelect = screen.getByDisplayValue(expectedSelectOptions[0].value)
    expect(venueSelect).toBeInTheDocument()
  })

  it('should render creation mode filter with default option selected', () => {
    renderOffers(props)

    expect(screen.getByDisplayValue('Tous')).toBeInTheDocument()
  })

  it('should render creation mode filter with given creation mode selected', () => {
    renderOffers({
      ...props,
      initialSearchFilters: {
        ...DEFAULT_SEARCH_FILTERS,
        creationMode: 'imported',
      },
    })

    expect(screen.getByDisplayValue('Synchronisé')).toBeInTheDocument()
  })

  it('should allow user to select manual creation mode filter', async () => {
    renderOffers(props)
    const creationModeSelect = screen.getByLabelText('Mode de création')

    await userEvent.selectOptions(creationModeSelect, 'Manuel')

    expect(screen.getByDisplayValue('Manuel')).toBeInTheDocument()
  })

  it('should allow user to select imported creation mode filter', async () => {
    renderOffers(props)
    const creationModeSelect = screen.getByDisplayValue('Tous')

    await userEvent.selectOptions(creationModeSelect, 'imported')

    expect(screen.getByDisplayValue('Synchronisé')).toBeInTheDocument()
  })

  it('should display event period filter with no default option', () => {
    renderOffers(props)

    const eventPeriodSelect = screen.queryAllByPlaceholderText('JJ/MM/AAAA')
    expect(eventPeriodSelect).toHaveLength(2)
  })

  it('should not display status filters modal', () => {
    renderOffers(props)

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
    renderOffers(props)

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
    renderOffers(props)
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

  it('should indicate that user has no offers yet', () => {
    renderOffers({ ...props, offers: [] })

    const noOffersText = screen.getByText('Vous n’avez pas encore créé d’offre')
    expect(noOffersText).toBeInTheDocument()
  })

  describe('when user is admin', () => {
    beforeEach(() => {
      props.currentUser.isAdmin = true
    })

    describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
      it('should disable status filters when no venue nor offerer filter is selected', () => {
        renderOffers(props)

        expect(
          screen.getByRole('button', {
            name: 'Statut Afficher ou masquer le filtre par statut',
          })
        ).toBeDisabled()
      })

      it('should disable status filters when no venue filter is selected, even if one venue filter is currently applied', async () => {
        renderOffers({
          ...props,
          initialSearchFilters: {
            ...DEFAULT_SEARCH_FILTERS,
            venueId: 'JI',
          },
        })

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
        renderOffers(props)
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
      it('should disable select all checkbox when no venue nor offerer filter is applied', () => {
        renderOffers(props, { user: currentUser })

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).toBeDisabled()
      })

      it('should disable select all checkbox when venue filter is not set', async () => {
        renderOffers(props, { user: currentUser })

        await userEvent.selectOptions(screen.getByLabelText('Lieu'), 'all')

        await userEvent.click(screen.getByText('Rechercher'))

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
          { user: currentUser }
        )

        await userEvent.selectOptions(screen.getByLabelText('Lieu'), 'JI')

        await userEvent.click(screen.getByText('Rechercher'))

        const selectAllOffersCheckbox =
          await screen.findByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).not.toBeDisabled()
      })

      it('should enable select all checkbox when offerer filter is applied', () => {
        renderOffers(
          {
            ...props,
            initialSearchFilters: {
              ...DEFAULT_SEARCH_FILTERS,
              offererId: 'A4',
            },
          },
          { user: currentUser }
        )

        const selectAllOffersCheckbox =
          screen.getByLabelText('Tout sélectionner')
        expect(selectAllOffersCheckbox).not.toBeDisabled()
      })
    })
  })

  it('should disabled checkbox when offer is rejected or pending for validation', () => {
    props.currentUser.isAdmin = false
    const offers = [
      listOffersOfferFactory({
        isActive: false,
        status: OfferStatus.REJECTED,
      }),
      listOffersOfferFactory({
        isActive: true,
        status: OfferStatus.PENDING,
      }),
      listOffersOfferFactory({
        isActive: true,
        status: OfferStatus.ACTIVE,
      }),
    ]

    renderOffers({ ...props, offers })

    expect(screen.queryByLabelText(offers[0].name)).toBeDisabled()
    expect(screen.queryByLabelText(offers[1].name)).toBeDisabled()
    expect(screen.queryByLabelText(offers[2].name)).toBeEnabled()
  })

  it('should not display the button to create an offer when user is an admin', () => {
    props.currentUser.isAdmin = true

    renderOffers(props)

    expect(screen.queryByText('Créer une offre')).toBeNull()
  })

  it('should display the button to create an offer when user is not an admin', async () => {
    const individualOffererNames = getOffererNameFactory()
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [individualOffererNames],
    })

    props.currentUser.isAdmin = false

    renderOffers(props)

    expect(
      await screen.findByRole('link', { name: 'Créer une offre' })
    ).toBeInTheDocument()
  })

  it('should not display button to create an offer when user is not yet validated', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
    })
    renderOffers(props)

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })

    expect(
      screen.queryByRole('link', { name: /Créer une offre/ })
    ).not.toBeInTheDocument()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<Offers {...props} />, { user: currentUser })

    const checkbox = screen.getByLabelText(offersRecap[0].name)
    await userEvent.click(checkbox)

    const actionBar = await screen.findByTestId('actions-bar')
    expect(actionBar).toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(actionBar).not.toBeInTheDocument()
  })

  describe('on click on select all offers checkbox', () => {
    it('should display display error message when trying to activate draft offers', async () => {
      const offers = [
        listOffersOfferFactory({
          isActive: false,
          status: OfferStatus.DRAFT,
        }),
      ]

      renderOffers({ ...props, offers })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des brouillons depuis cette liste'
      )
    })

    it('should display display error message when trying to activate collective offers with booking limit date passed', async () => {
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

      renderOffers({ ...props, audience: Audience.COLLECTIVE, offers })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
      )
    })

    it('should display success message activate inactive collective offer', async () => {
      const offers = [
        listOffersOfferFactory({
          isActive: false,
          hasBookingLimitDatetimesPassed: false,
        }),
      ]

      renderOffers({ ...props, audience: Audience.COLLECTIVE, offers })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(api.patchAllCollectiveOffersActiveStatus).toHaveBeenCalledTimes(1)
    })

    it('should check all validated offers checkboxes', async () => {
      // Given
      const offers = [
        listOffersOfferFactory(),
        listOffersOfferFactory(),
        listOffersOfferFactory({
          isActive: false,
          status: OfferStatus.REJECTED,
        }),
        listOffersOfferFactory({
          status: OfferStatus.PENDING,
        }),
      ]

      renderOffers({ ...props, offers })

      const firstOfferCheckbox = screen.getByLabelText(offers[0].name)
      const secondOfferCheckbox = screen.getByLabelText(offers[1].name)
      const thirdOfferCheckbox = screen.getByLabelText(offers[2].name)
      const fourthOfferCheckbox = screen.getByLabelText(offers[3].name)

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

  it('should display the collective offers format', () => {
    renderOffers({ ...props, audience: Audience.COLLECTIVE })

    expect(screen.getByRole('combobox', { name: 'Format' }))
  })

  it('should filter on the format', async () => {
    renderOffers({ ...props, audience: Audience.COLLECTIVE })

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

  it('should display the create offer button by default for non admins with validated offerers', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [{ ...getOfferManagingOffererFactory(), id: 1 }],
    })

    renderOffers(props)
    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })
    expect(screen.getByText(/Créer une offre/)).toBeInTheDocument()
  })

  it('should not display the create offer button', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [getOffererNameFactory()],
    })

    renderOffers(props, {}, true)
    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })
    expect(screen.queryByText(/Créer une offre/)).not.toBeInTheDocument()
  })
})
