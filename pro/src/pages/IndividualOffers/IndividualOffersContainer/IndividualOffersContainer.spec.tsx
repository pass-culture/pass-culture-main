import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import {
  GetOffererAddressResponseModel,
  ListOffersOfferResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import {
  ALL_OFFERER_ADDRESS_OPTION,
  ALL_VENUES_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import * as useNotification from 'commons/hooks/useNotification'
import { listOffersOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { offererAddressFactory } from 'commons/utils/factories/offererAddressFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { computeAddressDisplayName } from 'repository/venuesService'

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
  renderWithProviders(<IndividualOffersContainer {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: { selectedOffererId: 1, offererNames: [] },
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
    patchAllOffersActiveStatus: vi.fn(),
  },
}))

describe('IndividualOffersScreen', () => {
  let props: IndividualOffersContainerProps
  let offersRecap: ListOffersOfferResponseModel[]

  const mockNotifyError = vi.fn()
  const mockNotifyPending = vi.fn()
  const mockNotifySuccess = vi.fn()
  beforeEach(async () => {
    offersRecap = [listOffersOfferFactory()]

    props = {
      currentPageNumber: 1,
      isLoading: false,
      offers: offersRecap,
      initialSearchFilters: DEFAULT_SEARCH_FILTERS,
      redirectWithSelectedFilters: vi.fn(),
      venues: proVenuesOptions,
      offererAddresses: offererAddressOptions,
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

  it('should display column titles when offers are returned', () => {
    renderOffers(props)

    const headers = screen.getAllByRole('columnheader')
    expect(headers[0].textContent).toEqual('Tout sélectionner')
    expect(headers[1].textContent).toEqual('Nom de l’offre')
    expect(headers[2].textContent).toEqual('Lieu')
    expect(headers[3].textContent).toEqual('Stocks')
    expect(headers[4].textContent).toEqual('Statut')
    expect(headers[5].textContent).toEqual('Actions')
  })

  it('should render as much offers as returned by the api', () => {
    const firstOffer = listOffersOfferFactory()
    const secondOffer = listOffersOfferFactory()

    renderOffers({
      ...props,
      offers: [firstOffer, secondOffer],
    })

    expect(
      screen.getByLabelText(`Sélectionner l'offre "${firstOffer.name}"`)
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText(`Sélectionner l'offre "${secondOffer.name}"`)
    ).toBeInTheDocument()
  })

  it('should display an unchecked by default checkbox to select all offers when user is not admin', () => {
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
    offersRecap = Array.from({ length: 501 }, () => listOffersOfferFactory())

    renderOffers({
      ...props,
      offers: offersRecap,
    })

    screen.getByLabelText(`Sélectionner l'offre "${offersRecap[0].name}"`)
    expect(await screen.findByText('500+ offres')).toBeInTheDocument()
  })

  it('should send correct information when filling filter fields', async () => {
    const redirectWithSelectedFiltersSpy = vi.spyOn(props, 'redirectWithSelectedFilters')

    renderOffers(props)

    const searchAndChecked = async (params: Partial<SearchFiltersParams>) => {
      await userEvent.click(screen.getByText('Rechercher'))
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
      screen.getByRole('textbox', {
        name: LABELS.nameSearchInput,
      }),
    ).toBeInTheDocument()

    await userEvent.type(
      screen.getByRole('textbox', {
        name: LABELS.nameSearchInput,
      }),
      'Test'
    )

    await searchAndChecked({ nameOrIsbn: 'Test' })

    expect(screen.getByLabelText(/Lieu/)).toBeInTheDocument()
    await userEvent.selectOptions(screen.getByLabelText(/Lieu/), 'JI')

    await searchAndChecked({
      nameOrIsbn: 'Test',
      venueId: 'JI',
    })

    await userEvent.selectOptions(screen.getByLabelText(/Lieu/), 'JQ')

    await userEvent.click(screen.getByText('Rechercher'))

    await searchAndChecked({
      nameOrIsbn: 'Test',
      venueId: 'JQ',
    })

    expect(screen.getByLabelText(/Mode de création/)).toBeInTheDocument()

    await userEvent.selectOptions(
      screen.getByLabelText(/Mode de création/),
      'imported'
    )

    await searchAndChecked({
      nameOrIsbn: 'Test',
      venueId: 'JQ',
      creationMode: 'imported',
    })

    expect(screen.getByText(/Période de l’évènement/)).toBeInTheDocument()

    const [beginningDate, endingDate] =
      screen.getAllByPlaceholderText('JJ/MM/AAAA')
    await userEvent.type(beginningDate, '2025-02-02')
    await userEvent.type(endingDate, '2025-02-03')
    expect(beginningDate).toHaveValue('2025-02-02')
    expect(endingDate).toHaveValue('2025-02-03')

    await searchAndChecked({
      nameOrIsbn: 'Test',
      venueId: 'JQ',
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
      venueId: 'JQ',
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

    renderOffers(props, {
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    const addressSelect = screen.getByLabelText('Localisation')
    expect(addressSelect).not.toBeDisabled()

    const addressOptions = addressSelect.querySelectorAll('option')
    expect(addressOptions.length).toBe(expectedSelectOptions.length)
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

  describe('when user is admin', () => {
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
      renderOffers({
        ...props,
        initialSearchFilters: {
          ...DEFAULT_SEARCH_FILTERS,
          offererId: 'A4',
        },
      })

      const selectAllOffersCheckbox = screen.getByLabelText('Tout sélectionner')
      expect(selectAllOffersCheckbox).not.toBeDisabled()
    })
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

    expect(
      screen.queryByLabelText(`Sélectionner l'offre "${offers[0].name}"`)
    ).toBeDisabled()
    expect(
      screen.queryByLabelText(`Sélectionner l'offre "${offers[1].name}"`)
    ).toBeDisabled()
    expect(
      screen.queryByLabelText(`Sélectionner l'offre "${offers[2].name}"`)
    ).toBeEnabled()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<IndividualOffersContainer {...props} />)

    const checkbox = screen.getByLabelText(
      `Sélectionner l'offre "${offersRecap[0].name}"`
    )
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

      expect(mockNotifyPending).toHaveBeenCalledWith(
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

      const firstOfferCheckbox = screen.getByLabelText(
        `Sélectionner l'offre "${offers[0].name}"`
      )
      const secondOfferCheckbox = screen.getByLabelText(
        `Sélectionner l'offre "${offers[1].name}"`
      )
      const thirdOfferCheckbox = screen.getByLabelText(
        `Sélectionner l'offre "${offers[2].name}"`
      )
      const fourthOfferCheckbox = screen.getByLabelText(
        `Sélectionner l'offre "${offers[3].name}"`
      )

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
})
