import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { computeAddressDisplayName } from 'repository/venuesService'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import {
  GetOffererAddressResponseModel,
  ListOffersOfferResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  ALL_OFFERER_ADDRESS_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import { SearchFiltersParams } from '@/commons/core/Offers/types'
import * as useNotification from '@/commons/hooks/useNotification'
import {
  listOffersOfferFactory,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { offererAddressFactory } from '@/commons/utils/factories/offererAddressFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  IndividualOffersContainer,
  IndividualOffersContainerProps,
} from './IndividualOffersContainer'

const LABELS = {
  nameSearchInput: /Nom de l’offre/,
}

const renderOffers = (
  props: IndividualOffersContainerProps,
  options?: RenderWithProvidersOptions
) => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(
    <HeadlineOfferContextProvider>
      <IndividualOffersContainer {...props} />
    </HeadlineOfferContextProvider>,

    {
      user,
      storeOverrides: {
        user: {
          currentUser: user,
        },
        offerer: currentOffererFactory(),
      },
      ...options,
    }
  )
}

const categoriesAndSubcategories = {
  categories: [
    { id: 'CINEMA', proLabel: 'Cinéma', isSelectable: true },
    { id: 'JEU', proLabel: 'Jeux', isSelectable: true },
    { id: 'TECHNIQUE', proLabel: 'Technique', isSelectable: false },
  ],
  subcategories: [],
}

const offererAddress: GetOffererAddressResponseModel[] = [
  offererAddressFactory({
    label: 'Label',
  }),
  offererAddressFactory({
    city: 'New York',
  }),
]
const offererAddressOptions = [
  { value: '1', label: 'Label - 1 rue de paris 75001 Paris' },
  { value: '2', label: '1 rue de paris 75001 New York' },
]

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
    patchAllOffersActiveStatus: vi.fn(),
    getOffererHeadlineOffer: vi.fn(),
    getVenues: vi.fn(),
  },
}))

describe('IndividualOffersScreen', () => {
  let props: IndividualOffersContainerProps
  let offersRecap: ListOffersOfferResponseModel[]

  const mockNotifyError = vi.fn()
  const mockNotifyInfo = vi.fn()
  const mockNotifySuccess = vi.fn()
  beforeEach(async () => {
    offersRecap = [listOffersOfferFactory()]

    props = {
      currentPageNumber: 1,
      isLoading: false,
      offers: offersRecap,
      initialSearchFilters: DEFAULT_SEARCH_FILTERS,
      redirectWithSelectedFilters: vi.fn(),
      offererAddresses: offererAddressOptions,
      categories: categoriesAndSubcategories.categories.map(
        ({ id, proLabel }) => ({ value: id, label: proLabel })
      ),
    }

    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
      information: mockNotifyInfo,
      success: mockNotifySuccess,
    }))
  })

  it('should display column titles when offers are returned', () => {
    renderOffers(props)

    const headers = screen.getAllByRole('columnheader')
    expect(headers[1].textContent).toEqual('Nom de l’offre')
    expect(headers[2].textContent).toEqual('Localisation')
    expect(headers[3].textContent).toEqual('Stocks')
    expect(headers[4].textContent).toEqual('Statut')
    expect(headers[5].textContent).toEqual('Actions')
  })

  it('should display the Publication column if FF WIP_REFACTO_FUTURE_OFFER is enabled', () => {
    renderOffers(props, { features: ['WIP_REFACTO_FUTURE_OFFER'] })

    expect(
      screen.getByRole('columnheader', { name: 'Publication' })
    ).toBeInTheDocument()
  })

  it('should not display the Publication column if FF WIP_REFACTO_FUTURE_OFFER is disabled', () => {
    renderOffers(props)

    expect(
      screen.queryByRole('columnheader', { name: 'Publication' })
    ).not.toBeInTheDocument()
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

  it('should display an unchecked by default checkbox to select all offers', () => {
    const firstOffer = listOffersOfferFactory()
    const secondOffer = listOffersOfferFactory()

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
      offers: [...offersRecap, listOffersOfferFactory()],
    })

    screen.getByLabelText(offersRecap[0].name)
    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({
      ...props,
      offers: offersRecap,
    })

    screen.getByLabelText(offersRecap[0].name)
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 100+ for total number of offers if more than 500 offers are fetched', async () => {
    offersRecap = Array.from({ length: 101 }, () => listOffersOfferFactory())

    renderOffers({
      ...props,
      offers: offersRecap,
    })

    screen.getByLabelText(offersRecap[0].name)
    expect(await screen.findByText('100+ offres')).toBeInTheDocument()
  })

  it('should send correct information when filling filter fields', async () => {
    const redirectWithSelectedFiltersSpy = vi.spyOn(
      props,
      'redirectWithSelectedFilters'
    )

    renderOffers(props)

    const searchAndChecked = async (params: Partial<SearchFiltersParams>) => {
      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))
      expect(redirectWithSelectedFiltersSpy).toHaveBeenCalled()
      expect(redirectWithSelectedFiltersSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          ...DEFAULT_SEARCH_FILTERS,
          ...params,
        })
      )
    }

    await searchAndChecked({})

    expect(
      screen.getByRole('searchbox', {
        name: LABELS.nameSearchInput,
      })
    ).toBeInTheDocument()

    await userEvent.type(
      screen.getByRole('searchbox', {
        name: LABELS.nameSearchInput,
      }),
      'Test'
    )

    await searchAndChecked({ nameOrIsbn: 'Test' })

    expect(screen.getByLabelText(/Localisation/)).toBeInTheDocument()
    await userEvent.selectOptions(screen.getByLabelText(/Localisation/), '1')

    await searchAndChecked({
      nameOrIsbn: 'Test',
      offererAddressId: '1',
    })

    await userEvent.selectOptions(screen.getByLabelText(/Localisation/), '2')

    await userEvent.click(screen.getByText('Rechercher'))

    await searchAndChecked({
      nameOrIsbn: 'Test',
      offererAddressId: '2',
    })

    expect(screen.getByLabelText(/Mode de création/)).toBeInTheDocument()

    await userEvent.selectOptions(
      screen.getByLabelText(/Mode de création/),
      'imported'
    )

    await searchAndChecked({
      nameOrIsbn: 'Test',
      offererAddressId: '2',
      creationMode: 'imported',
    })

    expect(screen.getByText(/Période de l’évènement/)).toBeInTheDocument()

    const [beginningDate, endingDate] = screen.queryAllByLabelText(/période/)
    await userEvent.type(beginningDate, '2025-02-02')
    await userEvent.type(endingDate, '2025-02-03')
    expect(beginningDate).toHaveValue('2025-02-02')
    expect(endingDate).toHaveValue('2025-02-03')

    await searchAndChecked({
      nameOrIsbn: 'Test',
      offererAddressId: '2',
      creationMode: 'imported',
      periodBeginningDate: '2025-02-02',
      periodEndingDate: '2025-02-03',
    })

    expect(screen.getByTestId('wrapper-status')).toBeInTheDocument()
    await userEvent.selectOptions(
      within(screen.getByTestId('wrapper-status')).getByRole('combobox'),
      OfferStatus.ACTIVE
    )

    await searchAndChecked({
      nameOrIsbn: 'Test',
      offererAddressId: '2',
      creationMode: 'imported',
      periodBeginningDate: '2025-02-02',
      periodEndingDate: '2025-02-03',
      status: OfferStatus.ACTIVE,
    })

    expect(screen.getByText(/Réinitialiser les filtres/)).toBeInTheDocument()
    await userEvent.click(screen.getByText(/Réinitialiser les filtres/))

    await searchAndChecked({})

    redirectWithSelectedFiltersSpy.mockRestore()
  })

  it('should render offerer address filter with default option selected and given venues as options', () => {
    const expectedSelectOptions = [
      {
        id: [ALL_OFFERER_ADDRESS_OPTION.value],
        value: ALL_OFFERER_ADDRESS_OPTION.label,
      },
      {
        id: [offererAddress[0].id],
        value: computeAddressDisplayName(offererAddress[0]),
      },
      {
        id: [offererAddress[1].id],
        value: computeAddressDisplayName(offererAddress[1]),
      },
    ]

    renderOffers(props)

    const addressSelect = screen.getByLabelText('Localisation')
    expect(addressSelect).not.toBeDisabled()

    const addressOptions = addressSelect.querySelectorAll('option')
    expect(addressOptions.length).toBe(expectedSelectOptions.length)
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

    const eventPeriodSelect = screen.queryAllByLabelText(/période/)
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

    await userEvent.click(screen.getByText('Rechercher'))

    expect(screen.queryByText('Afficher les offres')).not.toBeInTheDocument()
  })

  it('should indicate that user has no offers yet', () => {
    renderOffers({ ...props, offers: [] })

    const noOffersText = screen.getByText('Vous n’avez pas encore créé d’offre')
    expect(noOffersText).toBeInTheDocument()
  })

  it('should disabled checkbox when offer is rejected or pending for validation', () => {
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
      offers: offers,
    })

    expect(screen.queryByLabelText(offers[0].name)).toBeDisabled()
    expect(screen.queryByLabelText(offers[1].name)).toBeDisabled()
    expect(screen.queryByLabelText(offers[2].name)).toBeEnabled()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<IndividualOffersContainer {...props} />)

    const checkbox = screen.getByLabelText(offersRecap[0].name)
    await userEvent.click(checkbox)

    const actionBar = await screen.findByTestId('actions-bar')
    expect(actionBar).toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(actionBar).not.toBeInTheDocument()
  })

  describe('on click on select all offers checkbox', () => {
    it('should activate only inactive offers when trying to activate draft or active offers', async () => {
      const offers = [
        listOffersOfferFactory({
          isActive: false,
          status: OfferStatus.DRAFT,
        }),
        listOffersOfferFactory({
          isActive: true,
          status: OfferStatus.ACTIVE,
        }),
        listOffersOfferFactory({
          isActive: false,
          status: OfferStatus.INACTIVE,
        }),
      ]

      renderOffers({
        ...props,
        offers: offers,
      })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))
      await userEvent.click(screen.getByText('Publier'))

      expect(mockNotifyInfo).toHaveBeenCalledWith(
        'Une offre est en cours d’activation, veuillez rafraichir dans quelques instants'
      )
      expect(api.patchAllOffersActiveStatus).toHaveBeenCalledWith({
        categoryId: null,
        creationMode: null,
        isActive: true,
        nameOrIsbn: null,
        offererAddressId: null,
        offererId: '1',
        periodBeginningDate: null,
        periodEndingDate: null,
        status: null,
        venueId: null,
      })
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
        offers: offers,
      })

      const firstOfferCheckbox = screen.getByLabelText(offers[0].name)
      const secondOfferCheckbox = screen.getByLabelText(offers[1].name)
      const thirdOfferCheckbox = screen.getByLabelText(offers[2].name)
      const fourthOfferCheckbox = screen.getByLabelText(offers[3].name)

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))

      expect(firstOfferCheckbox).toBeChecked()
      expect(secondOfferCheckbox).toBeChecked()
      expect(thirdOfferCheckbox).toBeDisabled()
      expect(fourthOfferCheckbox).toBeDisabled()

      await userEvent.click(screen.getByLabelText('Tout désélectionner'))

      expect(firstOfferCheckbox).not.toBeChecked()
      expect(secondOfferCheckbox).not.toBeChecked()
      expect(thirdOfferCheckbox).not.toBeChecked()
      expect(fourthOfferCheckbox).not.toBeChecked()
    })
  })

  it('should not display onboarding banner for archivage when we are in individual offer list ', () => {
    renderOffers(props)

    expect(
      screen.queryByText(
        'C’est nouveau ! Vous pouvez désormais archiver vos offres collectives.'
      )
    ).not.toBeInTheDocument()
  })

  it('should delete anyway even with active status', async () => {
    vi.spyOn(api, 'deleteDraftOffers').mockResolvedValueOnce()

    renderOffers({
      ...props,
      offers: [
        listOffersOfferFactory({ status: OfferStatus.ACTIVE }),
        listOffersOfferFactory({ status: OfferStatus.DRAFT }),
        listOffersOfferFactory({ status: OfferStatus.DRAFT }),
      ],
    })

    await userEvent.click(screen.getByText('Tout sélectionner'))
    await userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))
    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
    expect(mockNotifySuccess).toHaveBeenCalledWith(
      '2 brouillons ont bien été supprimés'
    )
  })

  it('should display headline offer block when feature is available', async () => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        venueListItemFactory({ name: 'Une venue physique & permanente' }),
      ],
    })
    vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue({
      id: 42,
      name: 'My offer',
      venueId: 1,
    })

    renderOffers(props)

    await waitFor(() => {
      expect(screen.getByText('Votre offre à la une')).toBeInTheDocument()
    })

    expect(screen.getByText('My offer')).toBeInTheDocument()
  })

  it('should display the publication and booking columns if the FF WIP_REFACTO_FUTURE_OFFER is enabled', () => {
    renderOffers(
      { ...props, offers: [listOffersOfferFactory()] },
      { features: ['WIP_REFACTO_FUTURE_OFFER'] }
    )

    expect(screen.getByText('Publication')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()
  })

  it('should not display the publication and booking columns if the FF WIP_REFACTO_FUTURE_OFFER is disabled', () => {
    renderOffers({ ...props, offers: [listOffersOfferFactory()] })

    expect(screen.queryByText('Publication')).not.toBeInTheDocument()
    expect(screen.queryByText('Réservations')).not.toBeInTheDocument()
  })
})
