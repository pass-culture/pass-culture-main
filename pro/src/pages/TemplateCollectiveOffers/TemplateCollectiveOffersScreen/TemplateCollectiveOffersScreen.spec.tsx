import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  type SharedCurrentUserResponseModel,
  UserRole,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import * as useNotification from '@/commons/hooks/useNotification'
import { collectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  TemplateCollectiveOffersScreen,
  type TemplateCollectiveOffersScreenProps,
} from './TemplateCollectiveOffersScreen'

const renderOffers = (
  props: TemplateCollectiveOffersScreenProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<TemplateCollectiveOffersScreen {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
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
  },
}))

const offers = [collectiveOfferTemplateFactory()]

const props = {
  currentPageNumber: 1,
  isLoading: false,
  offererId: '1',
  offers,
  urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  initialSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  redirectWithUrlFilters: vi.fn(),
}

describe('TemplateCollectiveOffersScreen', () => {
  let currentUser: SharedCurrentUserResponseModel

  const mockNotifyError = vi.fn()
  const mockNotifySuccess = vi.fn()
  beforeEach(async () => {
    currentUser = sharedCurrentUserFactory({
      roles: [UserRole.PRO],
    })

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
    const firstOffer = collectiveOfferTemplateFactory()
    const secondOffer = collectiveOfferTemplateFactory()

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
    const firstOffer = collectiveOfferTemplateFactory()
    const secondOffer = collectiveOfferTemplateFactory()

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
      offers: [...offers, collectiveOfferTemplateFactory()],
    })

    expect(
      screen.getByRole('checkbox', { name: offers[0].name })
    ).toBeInTheDocument()

    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })

  it('should display total number of offers in singular if one or no offer', async () => {
    renderOffers({
      ...props,
      offers,
    })

    expect(
      screen.getByRole('checkbox', { name: offers[0].name })
    ).toBeInTheDocument()
    expect(await screen.findByText('1 offre')).toBeInTheDocument()
  })

  it('should display 100+ for total number of offers if more than 500 offers are fetched', async () => {
    const offers = Array.from({ length: 101 }, () =>
      collectiveOfferTemplateFactory()
    )

    renderOffers({
      ...props,
      offers,
    })

    expect(
      screen.getByRole('checkbox', { name: offers[0].name })
    ).toBeInTheDocument()
    expect(await screen.findByText('100+ offres')).toBeInTheDocument()
  })

  it('should indicate that user has no offers yet', () => {
    renderOffers({ ...props, offers: [] })

    const noOffersText = screen.getByText('Vous n’avez pas encore créé d’offre')
    expect(noOffersText).toBeInTheDocument()
  })

  it('should not have "Tout Sélectionner" checked when there is no offer to be checked', async () => {
    const offers = [collectiveOfferTemplateFactory()]

    renderOffers({ ...props, offers })

    expect(await screen.findByLabelText('Tout sélectionner')).not.toBeChecked()
  })

  it('should display actionsBar when at least one offer is selected', async () => {
    renderWithProviders(<TemplateCollectiveOffersScreen {...props} />, {
      storeOverrides: {
        offerer: {
          currentOfferer: { ...defaultGetOffererResponseModel, id: 1 },
        },
      },
      user: currentUser,
    })

    const checkbox = screen.getByRole('checkbox', { name: offers[0].name })
    await userEvent.click(checkbox)

    const actionBar = await screen.findByTestId('actions-bar')
    expect(actionBar).toBeInTheDocument()

    await userEvent.click(checkbox)

    expect(actionBar).not.toBeInTheDocument()
  })

  describe('on click on select all offers checkbox', () => {
    it('should check all validated offers checkboxes', async () => {
      const offers = [
        collectiveOfferTemplateFactory({ name: 'offer 1' }),
        collectiveOfferTemplateFactory({ name: 'offer 2' }),
        collectiveOfferTemplateFactory({
          displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
          name: 'offer 3',
        }),
        collectiveOfferTemplateFactory({
          name: 'offer 4',
        }),
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
    it('should check all selectable offers checkboxes', async () => {
      const offer = collectiveOfferTemplateFactory({ name: 'offer 1' })
      const archivableOffer = collectiveOfferTemplateFactory({
        name: 'offer 2',
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      })
      const unselctableOffer = collectiveOfferTemplateFactory({
        name: 'offer 3',
        allowedActions: [],
      })

      renderOffers({
        ...props,
        offers: [offer, archivableOffer, unselctableOffer],
      })

      const firstOfferCheckbox = screen.getByRole('checkbox', {
        name: offer.name,
      })
      const secondOfferCheckbox = screen.getByRole('checkbox', {
        name: archivableOffer.name,
      })
      const thirdOfferCheckbox = screen.getByRole('checkbox', {
        name: unselctableOffer.name,
      })

      await userEvent.click(screen.getByLabelText('Tout sélectionner'))

      expect(firstOfferCheckbox).toBeChecked()
      expect(secondOfferCheckbox).toBeChecked()
      expect(thirdOfferCheckbox).not.toBeChecked()

      await userEvent.click(screen.getByLabelText('Tout désélectionner'))

      expect(firstOfferCheckbox).not.toBeChecked()
      expect(secondOfferCheckbox).not.toBeChecked()
      expect(thirdOfferCheckbox).not.toBeChecked()
    })
  })

  it('should filter on the format', async () => {
    renderOffers({
      ...props,
      offers: [collectiveOfferTemplateFactory()],
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

  it('should filter and sort column "Dates de l’évènement"', async () => {
    renderOffers({
      ...props,
      offers: [
        collectiveOfferTemplateFactory({
          dates: {
            start: '2024-07-31T09:11:00Z',
            end: '2024-07-31T09:11:00Z',
          },
        }),
        collectiveOfferTemplateFactory({
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

    const newFirstOfferEventDate =
      screen.getAllByTestId('offer-event-date')[0].textContent

    expect(newFirstOfferEventDate).toEqual('30/06/2024')
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
