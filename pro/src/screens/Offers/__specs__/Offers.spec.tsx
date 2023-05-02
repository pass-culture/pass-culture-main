import '@testing-library/jest-dom'

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { UserRole } from 'apiClient/v1'
import {
  ALL_CATEGORIES,
  ALL_EVENT_PERIODS,
  ALL_OFFERERS,
  ALL_OFFERS,
  ALL_STATUS,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_OFFER_TYPE,
  DEFAULT_CREATION_MODE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import * as useNotification from 'hooks/useNotification'
import { offererFactory } from 'utils/apiFactories'
import { individualOfferOffererFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Offers, { IOffersProps } from '../Offers'
import { individualOfferFactory } from '../utils/individualOffersFactories'

const renderOffers = (props: IOffersProps, storeOverrides: any) => {
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
  {
    id: 'JI',
    displayName: 'Ma venue',
  },
  {
    id: 'JQ',
    displayName: 'Mon offerer - Offre numérique',
  },
]

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: jest.fn().mockReturnValue({}),
    patchAllCollectiveOffersActiveStatus: jest.fn(),
  },
}))

describe('screen Offers', () => {
  let props: IOffersProps
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
    roles: Array<UserRole>
  }
  let store: any
  let offersRecap: Offer[]

  const mockNotifyError = jest.fn()
  const mockNotifyPending = jest.fn()
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
      loadAndUpdateOffers: jest.fn().mockResolvedValue(offersRecap),
      offerer: offererFactory(),
      offers: offersRecap,
      setIsLoading: jest.fn(),
      setOfferer: jest.fn(),
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
      separateIndividualAndCollectiveOffers: false,
      initialSearchFilters: DEFAULT_SEARCH_FILTERS,
      audience: Audience.INDIVIDUAL,
      redirectWithUrlFilters: jest.fn(),
      venues: proVenuesOptions,
      categories: categoriesAndSubcategories.categories.map(
        ({ id, proLabel }) => ({ id, displayName: proLabel })
      ),
    } as IOffersProps
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: mockNotifyError,
      pending: mockNotifyPending,
    }))
  })

  describe('render', () => {
    it('should load offers from API with defaults props', () => {
      // When
      renderOffers(props, store)

      // Then
      expect(props.loadAndUpdateOffers).toHaveBeenCalledWith({
        nameOrIsbn: ALL_OFFERS,
        venueId: ALL_VENUES,
        categoryId: ALL_CATEGORIES,
        offererId: ALL_OFFERERS,
        status: ALL_STATUS,
        creationMode: DEFAULT_CREATION_MODE.id,
        periodBeginningDate: ALL_EVENT_PERIODS,
        periodEndingDate: ALL_EVENT_PERIODS,
        collectiveOfferType: DEFAULT_COLLECTIVE_OFFER_TYPE.id,
      })
    })

    it('should display column titles when offers are returned', async () => {
      // When
      renderOffers(props, store)

      // Then
      expect(screen.getByText('Lieu', { selector: 'th' })).toBeInTheDocument()
      expect(screen.getByText('Stocks', { selector: 'th' })).toBeInTheDocument()
    })

    it('should render as much offers as returned by the api', async () => {
      // Given
      const firstOffer = individualOfferFactory()
      const secondOffer = individualOfferFactory()

      // When
      renderOffers(
        {
          ...props,
          offers: [firstOffer, secondOffer],
        },
        store
      )

      // Then
      const firstOfferLine = screen.getByText(firstOffer.name)
      expect(firstOfferLine).toBeInTheDocument()
      expect(screen.getByText(secondOffer.name)).toBeInTheDocument()
    })

    it('should display an unchecked by default checkbox to select all offers when user is not admin', async () => {
      // Given
      const firstOffer = individualOfferFactory()
      const secondOffer = individualOfferFactory()

      // When
      renderOffers(
        {
          ...props,
          currentUser: { ...props.currentUser, isAdmin: false },
          offers: [firstOffer, secondOffer],
        },
        store
      )

      // Then
      screen.getByText(firstOffer.name)
      const selectAllOffersCheckbox =
        screen.queryByLabelText('Tout sélectionner')
      expect(selectAllOffersCheckbox).toBeInTheDocument()
      expect(selectAllOffersCheckbox).not.toBeChecked()
      expect(selectAllOffersCheckbox).not.toBeDisabled()
    })

    describe('total number of offers', () => {
      it('should display total number of offers in plural if multiple offers', async () => {
        // When
        renderOffers(
          {
            ...props,
            offers: [...offersRecap, individualOfferFactory()],
          },
          store
        )

        // Then
        screen.getByText(offersRecap[0].name)
        expect(screen.getByText('2 offres')).toBeInTheDocument()
      })

      it('should display total number of offers in singular if one or no offer', async () => {
        // When
        renderOffers({ ...props, offers: offersRecap }, store)

        // Then
        screen.getByText(offersRecap[0].name)
        expect(await screen.findByText('1 offre')).toBeInTheDocument()
      })

      it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
        // Given
        offersRecap = Array.from({ length: 501 }, () =>
          individualOfferFactory()
        )

        // When
        renderOffers({ ...props, offers: offersRecap }, store)

        // Then
        screen.getByText(offersRecap[0].name)
        expect(await screen.findByText('500+ offres')).toBeInTheDocument()
      })
    })

    describe('filters', () => {
      it('should render venue filter with default option selected and given venues as options', async () => {
        // Given
        const expectedSelectOptions = [
          { id: [ALL_VENUES_OPTION.id], value: ALL_VENUES_OPTION.displayName },
          { id: [proVenues[0].id], value: proVenues[0].name },
          {
            id: [proVenues[1].id],
            value: `${proVenues[1].offererName} - Offre numérique`,
          },
        ]

        // When
        renderOffers(props, store)

        // Then
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
        // Given
        const expectedSelectOptions = [
          { id: [proVenues[0].id], value: proVenues[0].name },
        ]
        const filters = { ...DEFAULT_SEARCH_FILTERS, venueId: proVenues[0].id }

        // When
        renderOffers({ ...props, initialSearchFilters: filters }, store)

        // Then
        const venueSelect = screen.getByDisplayValue(
          expectedSelectOptions[0].value
        )
        expect(venueSelect).toBeInTheDocument()
      })

      it('should render creation mode filter with default option selected', async () => {
        // When
        renderOffers(props, store)

        // Then
        expect(screen.getByDisplayValue('Tous')).toBeInTheDocument()
      })

      it('should render creation mode filter with given creation mode selected', async () => {
        // When
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

        // Then
        expect(screen.getByDisplayValue('Synchronisé')).toBeInTheDocument()
      })

      it('should allow user to select manual creation mode filter', async () => {
        // Given
        renderOffers(props, store)
        const creationModeSelect = screen.getByLabelText('Mode de création')

        // When
        await userEvent.selectOptions(creationModeSelect, 'Manuel')

        // Then
        expect(screen.getByDisplayValue('Manuel')).toBeInTheDocument()
      })

      it('should allow user to select imported creation mode filter', async () => {
        // Given
        renderOffers(props, store)
        const creationModeSelect = screen.getByDisplayValue('Tous')

        // When
        await userEvent.selectOptions(creationModeSelect, 'imported')

        // Then
        expect(screen.getByDisplayValue('Synchronisé')).toBeInTheDocument()
      })

      it('should display event period filter with no default option', async () => {
        // When
        renderOffers(props, store)

        // Then
        const eventPeriodSelect = screen.queryAllByPlaceholderText('JJ/MM/AAAA')
        expect(eventPeriodSelect).toHaveLength(2)
      })

      describe('status filters', () => {
        it('should not display status filters modal', async () => {
          // When
          renderOffers(props, store)
          // Then
          expect(screen.getByText('Statut')).toBeInTheDocument()
          expect(
            screen.queryByText('Afficher les offres')
          ).not.toBeInTheDocument()
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
          // Given
          renderOffers(props, store)
          // When
          await userEvent.click(
            screen.getByAltText('Afficher ou masquer le filtre par statut')
          )
          // Then
          expect(screen.queryByText('Afficher les offres')).toBeInTheDocument()
          expect(screen.getByLabelText('Toutes')).toBeChecked()
          expect(screen.getByLabelText('Publiée')).not.toBeChecked()
          expect(screen.getByLabelText('Désactivée')).not.toBeChecked()
          expect(screen.getByLabelText('Épuisée')).not.toBeChecked()
          expect(screen.getByLabelText('Expirée')).not.toBeChecked()
          expect(screen.getByLabelText('Brouillon')).not.toBeChecked()
          expect(
            screen.getByLabelText('Validation en attente')
          ).not.toBeChecked()
          expect(screen.getByLabelText('Refusée')).not.toBeChecked()
          expect(
            screen.queryByText('Appliquer', { selector: 'button' })
          ).toBeInTheDocument()
        })

        it('should hide status filters when clicking outside the modal', async () => {
          // Given
          renderOffers(props, store)
          await userEvent.click(
            screen.getByAltText('Afficher ou masquer le filtre par statut')
          )
          // When
          await userEvent.click(
            screen.getByRole('heading', {
              name: 'Offres',
              level: 1,
            })
          )
          // Then
          expect(
            screen.queryByText('Afficher les offres')
          ).not.toBeInTheDocument()
        })

        it('should indicate that user has no offers yet', async () => {
          // When
          renderOffers({ ...props, offers: [] }, store)
          // Then
          const noOffersText = screen.getByText(
            'Vous n’avez pas encore créé d’offre.'
          )
          expect(noOffersText).toBeInTheDocument()
        })
      })

      describe('when user is admin', () => {
        beforeEach(() => {
          props.currentUser.isAdmin = true
        })
        describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
          it('should disable status filters when no venue nor offerer filter is selected', async () => {
            // When
            renderOffers(props, store)
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
          })

          it('should disable status filters when no venue filter is selected, even if one venue filter is currently applied', async () => {
            // Given
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
            // When
            await userEvent.selectOptions(
              screen.getByDisplayValue('Ma venue'),
              'all'
            )
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
          })

          it('should enable status filters when venue is selected but filter is not applied', async () => {
            // Given
            renderOffers(props, store)
            const venueOptionToSelect = screen.getByRole('option', {
              name: proVenues[0].name,
            })
            // When
            await userEvent.selectOptions(
              screen.getByLabelText('Lieu'),
              venueOptionToSelect
            )
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })
        })
        describe('select all offers checkbox', () => {
          it('should disable select all checkbox when no venue nor offerer filter is applied', async () => {
            // When
            renderOffers(props, store)
            // Then
            const selectAllOffersCheckbox =
              screen.getByLabelText('Tout sélectionner')
            expect(selectAllOffersCheckbox).toBeDisabled()
          })

          it('should not disable select all checkbox when no venue filter is selected but one is currently applied', async () => {
            // Given
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
            // When
            await userEvent.selectOptions(
              screen.getByDisplayValue('Ma venue'),
              'all'
            )
            // Then
            const selectAllOffersCheckbox =
              screen.getByLabelText('Tout sélectionner')
            expect(selectAllOffersCheckbox).not.toBeDisabled()
          })

          it('should disable select all checkbox when venue filter is selected but not applied', async () => {
            // Given
            renderOffers(props, store)
            // When
            await userEvent.selectOptions(
              screen.getByDisplayValue('Tous les lieux'),
              'JI'
            )
            // Then
            const selectAllOffersCheckbox =
              screen.getByLabelText('Tout sélectionner')
            expect(selectAllOffersCheckbox).toBeDisabled()
          })

          it('should enable select all checkbox when venue filter is applied', async () => {
            // When
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
            // Then
            const selectAllOffersCheckbox =
              screen.getByLabelText('Tout sélectionner')
            expect(selectAllOffersCheckbox).not.toBeDisabled()
          })
          it('should enable select all checkbox when offerer filter is applied', async () => {
            // When
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
            // Then
            const selectAllOffersCheckbox =
              screen.getByLabelText('Tout sélectionner')
            expect(selectAllOffersCheckbox).not.toBeDisabled()
          })
        })
      })
    })

    describe('when fraud detection', () => {
      it('should disabled checkbox when offer is rejected or pending for validation', async () => {
        // Given
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

        // When
        renderOffers({ ...props, offers }, store)

        // Then
        screen.getByText(offers[0].name)
        expect(
          screen.queryByTestId(`select-offer-${offers[0].id}`)
        ).toBeDisabled()
        expect(
          screen.queryByTestId(`select-offer-${offers[1].id}`)
        ).toBeDisabled()
        expect(
          screen.queryByTestId(`select-offer-${offers[2].id}`)
        ).toBeEnabled()
      })
    })
  })

  describe('on click on search button', () => {
    it('should load offers with default filters when no changes where made', async () => {
      // Given
      renderOffers(props, store)
      // When
      await userEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(props.loadAndUpdateOffers).toHaveBeenCalledWith({
        nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
        collectiveOfferType: DEFAULT_COLLECTIVE_OFFER_TYPE.id,
      })
    })
  })

  describe('button to create an offer', () => {
    it('should not be displayed when user is an admin', async () => {
      // Given
      props.currentUser.isAdmin = true

      // When
      await renderOffers(props, store)

      // Then
      expect(screen.queryByText('Créer une offre')).toBeNull()
    })

    it('should be displayed when user is not an admin', async () => {
      const individualOffererNames = individualOfferOffererFactory()
      jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [individualOffererNames],
      })

      // Given
      props.currentUser.isAdmin = false

      // When
      await renderOffers(props, store)

      expect(
        await screen.findByRole('link', { name: 'Créer une offre' })
      ).toBeInTheDocument()
    })

    it('should not be displayed when user is not yet validated', async () => {
      jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })

      // When
      await renderOffers(props, store)

      await waitFor(() => {
        expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
      })

      // Then
      expect(
        screen.queryByRole('link', { name: /Créer une offre/ })
      ).not.toBeInTheDocument()
    })
  })

  describe('offers selection', () => {
    it('should display actionsBar when at least one offer is selected', async () => {
      // Given
      renderWithProviders(<Offers {...props} />, { storeOverrides: store })

      // When
      const checkbox = screen.getByTestId(`select-offer-${offersRecap[0].id}`)
      await userEvent.click(checkbox)

      // Then
      const actionBar = await screen.findByTestId('actions-bar')
      expect(actionBar).toBeInTheDocument()

      // When
      await userEvent.click(checkbox)

      // Then
      expect(actionBar).not.toBeInTheDocument()
    })

    describe('on click on select all offers checkbox', () => {
      it('should display "Tout désélectionner" when initial label was "Tout sélectionner"', async () => {
        // Given
        renderOffers(props, store)

        // When
        await userEvent.click(screen.getByLabelText('Tout sélectionner'))

        // Then
        expect(
          screen.queryByLabelText('Tout désélectionner')
        ).toBeInTheDocument()
      })

      it('should display display error message when trying to activate draft offers', async () => {
        // Given
        const offers = [
          individualOfferFactory({
            isActive: false,
            status: 'DRAFT',
          }),
        ]

        renderOffers({ ...props, offers }, store)

        // When
        await userEvent.click(screen.getByLabelText('Tout sélectionner'))
        await userEvent.click(screen.getByText('Publier'))

        // Then
        expect(mockNotifyError).toHaveBeenCalledWith(
          'Vous ne pouvez pas publier des brouillons depuis cette liste'
        )
      })

      it('should display display error message when trying to activate collective offers with booking limit date passed', async () => {
        // Given
        const offers = [
          individualOfferFactory({
            isActive: false,
            hasBookingLimitDatePassed: true,
          }),
        ]

        renderOffers({ ...props, audience: Audience.COLLECTIVE, offers }, store)

        // When
        await userEvent.click(screen.getByLabelText('Tout sélectionner'))
        await userEvent.click(screen.getByText('Publier'))

        // Then
        expect(mockNotifyError).toHaveBeenCalledWith(
          'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
        )
      })

      it('should display success message activate inactive collective offer', async () => {
        // Given
        const offers = [
          individualOfferFactory({
            isActive: false,
            hasBookingLimitDatetimesPassed: false,
          }),
        ]

        renderOffers({ ...props, audience: Audience.COLLECTIVE, offers }, store)

        // When
        await userEvent.click(screen.getByLabelText('Tout sélectionner'))
        await userEvent.click(screen.getByText('Publier'))

        // Then
        expect(api.patchAllCollectiveOffersActiveStatus).toHaveBeenCalledTimes(
          1
        )
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

        // When
        await userEvent.click(screen.getByLabelText('Tout sélectionner'))

        // Then
        expect(firstOfferCheckbox).toBeChecked()
        expect(secondOfferCheckbox).toBeChecked()
        expect(thirdOfferCheckbox).not.toBeChecked()
        expect(fourthOfferCheckbox).not.toBeChecked()

        // When
        await userEvent.click(screen.getByLabelText('Tout désélectionner'))

        // Then
        expect(firstOfferCheckbox).not.toBeChecked()
        expect(secondOfferCheckbox).not.toBeChecked()
        expect(thirdOfferCheckbox).not.toBeChecked()
        expect(fourthOfferCheckbox).not.toBeChecked()
      })
    })
  })
})
