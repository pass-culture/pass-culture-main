import '@testing-library/jest-dom'

import {
  ALL_CATEGORIES,
  ALL_EVENT_PERIODS,
  ALL_OFFERERS,
  ALL_OFFERS,
  ALL_STATUS,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  DEFAULT_CREATION_MODE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { MemoryRouter, Router } from 'react-router'
import Offers, { IOffersProps } from '../Offers'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { offerFactory, offererFactory } from 'utils/apiFactories'

import { Audience } from 'core/shared'
import { Offer } from 'core/Offers/types'
import { Provider } from 'react-redux'
import React from 'react'
import type { Store } from 'redux'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import { createMemoryHistory } from 'history'
import { queryByTextTrimHtml } from 'utils/testHelpers'
import userEvent from '@testing-library/user-event'

const renderOffers = (props: IOffersProps, store: Store) => {
  const history = createMemoryHistory()
  return {
    ...render(
      <Provider store={store}>
        <Router history={history}>
          <Offers {...props} />
        </Router>
      </Provider>
    ),
    history,
  }
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

jest.mock('apiClient/api', () => ({
  api: {
    listOffers: jest.fn(),
    getCategories: jest.fn().mockResolvedValue(categoriesAndSubcategories),
  },
}))

jest.mock('routes/Offers/adapters/getFilteredOffersAdapter', () => jest.fn())

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

describe('screen Offers', () => {
  let props: IOffersProps
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
    publicName: string
  }
  let store: Store
  let offersRecap: Offer[]

  beforeEach(() => {
    currentUser = {
      id: 'EY',
      isAdmin: false,
      name: 'Current User',
      publicName: 'USER',
    }
    store = configureTestStore({
      data: {
        users: [currentUser],
      },
      user: {
        initialized: true,
      },
      offers: {
        searchFilters: DEFAULT_SEARCH_FILTERS,
      },
    })
    offersRecap = [offerFactory({ venue: proVenues[0] })]
    ;(api.listOffers as jest.Mock).mockResolvedValue(offersRecap)

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
      })
    })

    it('should display column titles when offers are returned', async () => {
      // When
      renderOffers(props, store)

      // Then
      await expect(
        screen.findByText('Lieu', { selector: 'th' })
      ).resolves.toBeInTheDocument()
      expect(screen.getByText('Stocks', { selector: 'th' })).toBeInTheDocument()
    })

    it('should render as much offers as returned by the api', async () => {
      // Given
      const firstOffer = offerFactory()
      const secondOffer = offerFactory()

      // When
      renderOffers(
        {
          ...props,
          offers: [firstOffer, secondOffer],
        },
        store
      )

      // Then
      const firstOfferLine = await screen.findByText(firstOffer.name)
      expect(firstOfferLine).toBeInTheDocument()
      expect(screen.getByText(secondOffer.name)).toBeInTheDocument()
    })

    it('should display an unchecked by default checkbox to select all offers when user is not admin', async () => {
      // Given
      const firstOffer = offerFactory()
      const secondOffer = offerFactory()

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
      await screen.findByText(firstOffer.name)
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
            offers: [...offersRecap, offerFactory()],
          },
          store
        )

        // Then
        await screen.findByText(offersRecap[0].name)
        expect(queryByTextTrimHtml(screen, '2 offres')).toBeInTheDocument()
      })

      it('should display total number of offers in singular if one or no offer', async () => {
        // When
        renderOffers({ ...props, offers: offersRecap }, store)

        // Then
        await screen.findByText(offersRecap[0].name)
        expect(queryByTextTrimHtml(screen, '1 offre')).toBeInTheDocument()
      })

      it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
        // Given
        offersRecap = Array.from({ length: 501 }, () => offerFactory())

        // When
        renderOffers({ ...props, offers: offersRecap }, store)

        // Then
        await screen.findByText(offersRecap[0].name)
        expect(queryByTextTrimHtml(screen, '500\\+ offres')).toBeInTheDocument()
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

        const firstVenueOption = await screen.findByRole('option', {
          name: expectedSelectOptions[1].value,
        })
        expect(firstVenueOption).toBeInTheDocument()

        const secondVenueOption = await screen.findByRole('option', {
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
        const venueSelect = await screen.findByDisplayValue(
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
        expect(screen.getByDisplayValue('Importée')).toBeInTheDocument()
      })

      it('should allow user to select manual creation mode filter', async () => {
        // Given
        renderOffers(props, store)
        const creationModeSelect = screen.getByLabelText('Mode de création')

        // When
        userEvent.selectOptions(creationModeSelect, 'Manuelle')

        // Then
        await waitFor(() =>
          expect(screen.getByDisplayValue('Manuelle')).toBeInTheDocument()
        )
      })

      it('should allow user to select imported creation mode filter', () => {
        // Given
        renderOffers(props, store)
        const creationModeSelect = screen.getByDisplayValue('Tous')

        // When
        fireEvent.change(creationModeSelect, { target: { value: 'imported' } })

        // Then
        expect(screen.getByDisplayValue('Importée')).toBeInTheDocument()
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
          await expect(screen.findByText('Statut')).resolves.toBeInTheDocument()
          expect(
            screen.queryByText('Afficher les statuts')
          ).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Tous')).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Active')).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Inactive')).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Épuisée')).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Expirée')).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Appliquer')).not.toBeInTheDocument()
          expect(
            screen.queryByLabelText('Validation en attente')
          ).not.toBeInTheDocument()
          expect(screen.queryByLabelText('Refusée')).not.toBeInTheDocument()
        })

        it('should display status filters with "Tous" as default value when clicking on "Statut" filter icon', async () => {
          // Given
          renderOffers(props, store)
          // When
          fireEvent.click(
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )
          // Then
          expect(screen.queryByText('Afficher les statuts')).toBeInTheDocument()
          expect(screen.getByLabelText('Tous')).toBeChecked()
          expect(screen.getByLabelText('Active')).not.toBeChecked()
          expect(screen.getByLabelText('Inactive')).not.toBeChecked()
          expect(screen.getByLabelText('Épuisée')).not.toBeChecked()
          expect(screen.getByLabelText('Expirée')).not.toBeChecked()
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
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )
          // When
          await userEvent.click(
            screen.getByRole('heading', {
              name: 'Offres',
              level: 1,
            })
          )
          // Then
          expect(screen.queryByText('Afficher les statuts')).toBeNull()
        })

        it('should indicate that user has no offers yet', async () => {
          // When
          renderOffers({ ...props, offers: [] }, store)
          // Then
          const noOffersText = await screen.findByText(
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
            const statusFiltersIcon = await screen.findByAltText(
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
            fireEvent.change(await screen.findByDisplayValue('Ma venue'), {
              target: { value: 'all' },
            })
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
          })

          it('should enable status filters when venue is selected but filter is not applied', async () => {
            // Given
            renderOffers(props, store)
            const venueOptionToSelect = await screen.findByRole('option', {
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
            const selectAllOffersCheckbox = await screen.findByLabelText(
              'Tout sélectionner'
            )
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
              configureTestStore({
                data: {
                  users: [currentUser],
                },
                user: {
                  initialized: true,
                },
                offers: {
                  searchFilters: { ...DEFAULT_SEARCH_FILTERS, venueId: 'JI' },
                },
              })
            )
            // When
            fireEvent.change(await screen.findByDisplayValue('Ma venue'), {
              target: { value: 'all' },
            })
            // Then
            const selectAllOffersCheckbox =
              screen.getByLabelText('Tout sélectionner')
            expect(selectAllOffersCheckbox).not.toBeDisabled()
          })

          it('should disable select all checkbox when venue filter is selected but not applied', async () => {
            // Given
            renderOffers(props, store)
            // When
            fireEvent.change(
              await screen.findByDisplayValue('Tous les lieux'),
              {
                target: { value: 'JI' },
              }
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
              configureTestStore({
                data: {
                  users: [currentUser],
                },
                user: {
                  initialized: true,
                },
                offers: {
                  searchFilters: { ...DEFAULT_SEARCH_FILTERS, venueId: 'IJ' },
                },
              })
            )
            // Then
            const selectAllOffersCheckbox = await screen.findByLabelText(
              'Tout sélectionner'
            )
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
              configureTestStore({
                data: {
                  users: [currentUser],
                },
                user: {
                  initialized: true,
                },
                offers: {
                  searchFilters: { ...DEFAULT_SEARCH_FILTERS, offererId: 'A4' },
                },
              })
            )
            // Then
            const selectAllOffersCheckbox = await screen.findByLabelText(
              'Tout sélectionner'
            )
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
          offerFactory({
            isActive: false,
            status: 'REJECTED',
          }),
          offerFactory({
            isActive: true,
            status: 'PENDING',
          }),
          offerFactory({
            isActive: true,
            status: 'ACTIVE',
          }),
        ]

        // When
        renderOffers({ ...props, offers }, store)

        // Then
        await screen.findByText(offers[0].name)
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
      fireEvent.click(screen.getByText('Lancer la recherche'))
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
      })
    })
  })

  describe('button to create an offer', () => {
    it('should not be displayed when user is an admin', () => {
      // Given
      props.currentUser.isAdmin = true

      // When
      renderOffers(props, store)

      // Then
      expect(screen.queryByText('Créer une offre')).toBeNull()
    })

    it('should be displayed when user is not an admin', () => {
      // Given
      props.currentUser.isAdmin = false

      // When
      renderOffers(props, store)

      // Then
      const createLink = queryByTextTrimHtml(screen, 'Créer une offre', {
        selector: 'a',
        leafOnly: false,
      })
      expect(createLink).not.toBeNull()
    })
  })

  describe('offers selection', () => {
    it('should display actionsBar when at least one offer is selected', async () => {
      // Given
      render(
        <Provider store={store}>
          <MemoryRouter>
            <Offers {...props} />
          </MemoryRouter>
        </Provider>
      )

      const actionBar = await screen.findByTestId('actions-bar')

      // When
      const checkbox = await screen.findByTestId(
        `select-offer-${offersRecap[0].id}`
      )
      await userEvent.click(checkbox)

      // Then
      expect(actionBar).toHaveClass('actions-bar-visible')

      // When
      await userEvent.click(checkbox)

      // Then
      expect(actionBar).not.toHaveClass('actions-bar-visible')
    })

    describe('on click on select all offers checkbox', () => {
      it('should display "Tout désélectionner" when initial label was "Tout sélectionner"', async () => {
        // Given
        renderOffers(props, store)

        // When
        fireEvent.click(await screen.findByLabelText('Tout sélectionner'))

        // Then
        expect(
          screen.queryByLabelText('Tout désélectionner')
        ).toBeInTheDocument()
      })

      it('should check all validated offers checkboxes', async () => {
        // Given
        const offers = [
          offerFactory(),
          offerFactory({
            isFullyBooked: true,
          }),
          offerFactory({
            isActive: false,
            status: 'REJECTED',
          }),
          offerFactory({
            status: 'PENDING',
          }),
        ]

        renderOffers({ ...props, offers }, store)

        const firstOfferCheckbox = await screen.findByTestId(
          `select-offer-${offers[0].id}`
        )
        const secondOfferCheckbox = await screen.findByTestId(
          `select-offer-${offers[1].id}`
        )
        const thirdOfferCheckbox = await screen.findByTestId(
          `select-offer-${offers[2].id}`
        )
        const fourthOfferCheckbox = await screen.findByTestId(
          `select-offer-${offers[3].id}`
        )

        // When
        fireEvent.click(screen.getByLabelText('Tout sélectionner'))

        // Then
        expect(firstOfferCheckbox).toBeChecked()
        expect(secondOfferCheckbox).toBeChecked()
        expect(thirdOfferCheckbox).not.toBeChecked()
        expect(fourthOfferCheckbox).not.toBeChecked()

        // When
        fireEvent.click(screen.getByLabelText('Tout désélectionner'))

        // Then
        expect(firstOfferCheckbox).not.toBeChecked()
        expect(secondOfferCheckbox).not.toBeChecked()
        expect(thirdOfferCheckbox).not.toBeChecked()
        expect(fourthOfferCheckbox).not.toBeChecked()
      })
    })
  })
})
