import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  CollectiveOfferStatus,
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
    deleteDraftOffers: vi.fn(),
  },
}))

describe('screen Offers', () => {
  let props: OffersProps
  let currentUser: SharedCurrentUserResponseModel
  let offersRecap: ListOffersOfferResponseModel[]

  const mockNotifyError = vi.fn()
  const mockNotifyPending = vi.fn()
  const mockNotifySuccess = vi.fn()
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
      individualOffers: offersRecap,
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
      success: mockNotifySuccess,
    }))
  })

  it('should display column titles when offers are returned', () => {
    renderOffers(props)

    const headers = screen.getAllByRole('columnheader')
    expect(headers[1].textContent).toEqual('Lieu')
    expect(headers[2].textContent).toEqual('Stocks')
    expect(headers[3].textContent).toEqual('Statut')
    expect(headers[4].textContent).toEqual('Actions')
  })

  it('should render as much offers as returned by the api', () => {
    const firstOffer = listOffersOfferFactory()
    const secondOffer = listOffersOfferFactory()

    renderOffers({
      ...props,
      audience: Audience.INDIVIDUAL,
      individualOffers: [firstOffer, secondOffer],
    })

    expect(screen.getByLabelText(firstOffer.name)).toBeInTheDocument()
    expect(screen.getByLabelText(secondOffer.name)).toBeInTheDocument()
  })

  it('should display an unchecked by default checkbox to select all offers when user is not admin', () => {
    const firstOffer = listOffersOfferFactory()
    const secondOffer = listOffersOfferFactory()

    renderOffers({
      ...props,
      audience: Audience.INDIVIDUAL,
      currentUser: { ...props.currentUser, isAdmin: false },
      individualOffers: [firstOffer, secondOffer],
    })

    const selectAllOffersCheckbox = screen.queryByLabelText('Tout sélectionner')
    expect(selectAllOffersCheckbox).toBeInTheDocument()
    expect(selectAllOffersCheckbox).not.toBeChecked()
    expect(selectAllOffersCheckbox).not.toBeDisabled()
  })

  it('should display total number of offers in plural if multiple offers', () => {
    renderOffers({
      ...props,
      audience: Audience.INDIVIDUAL,
      individualOffers: [...offersRecap, listOffersOfferFactory()],
    })

    screen.getByLabelText(offersRecap[0].name)
    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({
      ...props,
      audience: Audience.INDIVIDUAL,
      individualOffers: offersRecap,
    })

    screen.getByLabelText(offersRecap[0].name)
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
    offersRecap = Array.from({ length: 501 }, () => listOffersOfferFactory())

    renderOffers({
      ...props,
      audience: Audience.INDIVIDUAL,
      individualOffers: offersRecap,
    })

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
    const creationModeSelect = screen.getByRole('combobox', {
      name: 'Mode de création',
    })

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

    expect(
      screen.getByRole('combobox', {
        name: 'Statut Nouveau',
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
        name: 'Statut Nouveau',
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
    renderOffers({ ...props, individualOffers: [] })

    const noOffersText = screen.getByText('Vous n’avez pas encore créé d’offre')
    expect(noOffersText).toBeInTheDocument()
  })

  describe('when user is admin', () => {
    beforeEach(() => {
      props.currentUser.isAdmin = true
    })

    it('should not be able to check all offers for performance reasons', () => {
      renderOffers({ ...props, isRestrictedAsAdmin: true })

      const selectAllOffersCheckbox = screen.getByLabelText('Tout sélectionner')
      expect(selectAllOffersCheckbox).toBeDisabled()
    })

    it('should be able to check all offers because, a venue being filtered, there are no performance issues', async () => {
      renderOffers({
        ...props,
        isRestrictedAsAdmin: false,
      })

      await userEvent.selectOptions(screen.getByLabelText('Lieu'), 'JI')

      await userEvent.click(screen.getByText('Rechercher'))

      const selectAllOffersCheckbox =
        await screen.findByLabelText('Tout sélectionner')
      expect(selectAllOffersCheckbox).not.toBeDisabled()
    })

    it('should be able to check all offers because, a offerer being filtered, there are no performance issues', () => {
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

      const selectAllOffersCheckbox = screen.getByLabelText('Tout sélectionner')
      expect(selectAllOffersCheckbox).not.toBeDisabled()
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

    renderOffers({
      ...props,
      individualOffers: offers,
      audience: Audience.INDIVIDUAL,
    })

    expect(screen.queryByLabelText(offers[0].name)).toBeDisabled()
    expect(screen.queryByLabelText(offers[1].name)).toBeDisabled()
    expect(screen.queryByLabelText(offers[2].name)).toBeEnabled()
  })

  it('should not have "Tout Sélectionner" checked when there is no offer to be checked', () => {
    const offers = [
      collectiveOfferFactory({
        isActive: false,
        status: CollectiveOfferStatus.PENDING,
      }),
    ]

    renderOffers({
      ...props,
      audience: Audience.COLLECTIVE,
      collectiveOffers: offers,
    })

    expect(screen.getByLabelText('Tout sélectionner')).not.toBeChecked()
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

      renderOffers({
        ...props,
        individualOffers: offers,
        audience: Audience.INDIVIDUAL,
      })

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

      renderOffers({
        ...props,
        audience: Audience.COLLECTIVE,
        collectiveOffers: offers,
      })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
      )
    })

    it('should display success message activate inactive collective offer', async () => {
      const offers = [
        collectiveOfferFactory({
          isActive: false,
          hasBookingLimitDatetimesPassed: false,
        }),
      ]

      renderOffers({
        ...props,
        audience: Audience.COLLECTIVE,
        collectiveOffers: offers,
      })

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
          isEditable: false,
        }),
        listOffersOfferFactory({
          status: OfferStatus.PENDING,
          isEditable: false,
        }),
      ]

      renderOffers({
        ...props,
        individualOffers: offers,
        audience: Audience.INDIVIDUAL,
      })

      const firstOfferCheckbox = screen.getByLabelText(offers[0].name)
      const secondOfferCheckbox = screen.getByLabelText(offers[1].name)
      const thirdOfferCheckbox = screen.getByLabelText(offers[2].name)
      const fourthOfferCheckbox = screen.getByLabelText(offers[3].name)

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

  it('should display the collective offers format', () => {
    renderOffers({
      ...props,
      collectiveOffers: [collectiveOfferFactory()],
      audience: Audience.COLLECTIVE,
    })
    expect(screen.getByRole('combobox', { name: 'Format' }))
  })

  it('should filter on the format', async () => {
    renderOffers({
      ...props,
      collectiveOffers: [collectiveOfferFactory()],
      audience: Audience.COLLECTIVE,
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

  it('should display onboarding banner for archivage only in collective offer list', () => {
    renderOffers({
      ...props,
      audience: Audience.COLLECTIVE,
      collectiveOffers: [],
    })

    expect(
      screen.getByText(
        'C’est nouveau ! Vous pouvez désormais archiver vos offres collectives.'
      )
    ).toBeInTheDocument()
  })

  it('should not display onboarding banner for archivage when we are in individual offer list ', () => {
    renderOffers(props)

    expect(
      screen.queryByText(
        'C’est nouveau ! Vous pouvez désormais archiver vos offres collectives.'
      )
    ).not.toBeInTheDocument()
  })

  it('should notify when deleting offers there are not draft', async () => {
    renderOffers({
      ...props,
      individualOffers: [
        listOffersOfferFactory({ status: OfferStatus.ACTIVE }),
      ],
      audience: Audience.INDIVIDUAL,
    })

    await userEvent.click(screen.getByText('Tout sélectionner'))
    await userEvent.click(screen.getByText('Supprimer'))

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Seuls les brouillons peuvent être supprimés'
    )
  })

  it('should delete aniway even with active status', async () => {
    vi.spyOn(api, 'deleteDraftOffers').mockResolvedValueOnce()

    renderOffers({
      ...props,
      individualOffers: [
        listOffersOfferFactory({ status: OfferStatus.ACTIVE }),
        listOffersOfferFactory({ status: OfferStatus.DRAFT }),
        listOffersOfferFactory({ status: OfferStatus.DRAFT }),
      ],
      audience: Audience.INDIVIDUAL,
    })

    await userEvent.click(screen.getByText('Tout sélectionner'))
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer' })[2]
    )
    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
    expect(mockNotifySuccess).toHaveBeenCalledWith(
      'Les brouillons ont bien été supprimés'
    )
  })

  it('should display a new column "Date de l’évènement" if FF is enabled', () => {
    const featureOverrides = {
      features: ['ENABLE_COLLECTIVE_OFFERS_EXPIRATION'],
    }

    renderOffers(
      {
        ...props,
        collectiveOffers: [collectiveOfferFactory()],
        audience: Audience.COLLECTIVE,
      },
      featureOverrides
    )

    expect(screen.getByText('Date de l’évènement'))
  })

  it('should filter new column "Date de l’évènement"', async () => {
    const featureOverrides = {
      features: ['ENABLE_COLLECTIVE_OFFERS_EXPIRATION'],
    }

    renderOffers(
      {
        ...props,
        collectiveOffers: [
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
        audience: Audience.COLLECTIVE,
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
})
