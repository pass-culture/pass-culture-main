/*
 * @debt complexity "Gaël: file over 300 lines"
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 */

import '@testing-library/jest-dom'
import { parse } from 'querystring'

import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Router } from 'react-router'

import {
  ALL_OFFERERS,
  ALL_OFFERS,
  ALL_STATUS,
  ALL_CATEGORIES,
  ALL_CATEGORIES_OPTION,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  ALL_EVENT_PERIODS,
  CREATION_MODES_FILTERS,
  DEFAULT_CREATION_MODE,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'components/pages/Offers/Offers/_constants'
import Offers from 'components/pages/Offers/Offers/Offers'
import * as pcapi from 'repository/pcapi/pcapi'
import { fetchAllVenuesByProUser } from 'repository/venuesService'
import { configureTestStore } from 'store/testUtils'
import { offerFactory } from 'utils/apiFactories'
import { queryByTextTrimHtml, renderWithStyles } from 'utils/testHelpers'

import { computeOffersUrl } from '../../utils/computeOffersUrl'

const renderOffers = (props, store, filters = DEFAULT_SEARCH_FILTERS) => {
  const history = createMemoryHistory()
  const route = computeOffersUrl(filters)
  history.push(route)
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

jest.mock('repository/venuesService', () => ({
  ...jest.requireActual('repository/venuesService'),
  fetchAllVenuesByProUser: jest.fn(),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  loadFilteredOffers: jest.fn(),
  loadCategories: jest.fn().mockResolvedValue(categoriesAndSubcategories),
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

describe('src | components | pages | Offers | Offers', () => {
  let props
  let currentUser
  let store
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
  let offersRecap

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
    })
    offersRecap = [offerFactory({ venue: proVenues[0] })]

    pcapi.loadFilteredOffers.mockResolvedValue(offersRecap)

    props = {
      currentUser,
      getOfferer: jest.fn().mockResolvedValue({}),
    }
    fetchAllVenuesByProUser.mockResolvedValue(proVenues)
  })

  describe('render', () => {
    it('should load offers from API with defaults props', () => {
      // When
      renderOffers(props, store)

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
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
      expect(screen.getByText('Stock', { selector: 'th' })).toBeInTheDocument()
    })

    it('should not display column titles when no offers are returned', async () => {
      // Given
      props.offers = []

      // When
      renderOffers(props, store)

      // Then
      expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
      expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
    })

    it('should render as much offers as returned by the api', async () => {
      // Given
      const firstOffer = offerFactory()
      const secondOffer = offerFactory()
      pcapi.loadFilteredOffers.mockResolvedValue([firstOffer, secondOffer])

      // When
      await renderOffers(props, store)

      // Then
      const firstOfferLine = await screen.findByText(firstOffer.name)
      expect(firstOfferLine).toBeInTheDocument()
      expect(screen.getByText(secondOffer.name)).toBeInTheDocument()
    })

    it('should display an unchecked by default checkbox to select all offers when user is not admin', async () => {
      // Given
      props.currentUser.isAdmin = false
      const firstOffer = offerFactory()
      const secondOffer = offerFactory()
      pcapi.loadFilteredOffers.mockResolvedValue([firstOffer, secondOffer])

      // When
      await renderOffers(props, store)

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
        // Given
        pcapi.loadFilteredOffers.mockResolvedValueOnce([
          ...offersRecap,
          offerFactory(),
        ])

        // When
        renderOffers(props, store)

        // Then
        await screen.findByText(offersRecap[0].name)
        expect(queryByTextTrimHtml(screen, '2 offres')).toBeInTheDocument()
      })

      it('should display total number of offers in singular if one or no offer', async () => {
        // Given
        pcapi.loadFilteredOffers.mockResolvedValueOnce(offersRecap)

        // When
        renderOffers(props, store)

        // Then
        await screen.findByText(offersRecap[0].name)
        expect(queryByTextTrimHtml(screen, '1 offre')).toBeInTheDocument()
      })

      it('should display 500+ for total number of offers if more than 500 offers are fetched', async () => {
        // Given
        offersRecap = Array.from({ length: 501 }, offerFactory)
        pcapi.loadFilteredOffers.mockResolvedValueOnce(offersRecap)

        // When
        renderOffers(props, store)

        // Then
        await screen.findByText(offersRecap[0].name)
        expect(queryByTextTrimHtml(screen, '500\\+ offres')).toBeInTheDocument()
      })
    })

    describe('filters', () => {
      it('should display only selectable categories on filters', async () => {
        // When
        renderOffers(props, store)

        // Then
        await expect(
          screen.findByRole('option', { name: 'Cinéma' })
        ).resolves.toBeInTheDocument()
        await expect(
          screen.findByRole('option', { name: 'Jeux' })
        ).resolves.toBeInTheDocument()
        await expect(
          screen.findByRole('option', { name: 'Technique' })
        ).rejects.toBeTruthy()
      })

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
        const filters = { lieu: proVenues[0].id }

        // When
        await renderOffers(props, store, filters)

        // Then
        let venueSelect = screen.getByDisplayValue(
          expectedSelectOptions[0].value,
          {
            selector: 'select[name="lieu"]',
          }
        )
        expect(venueSelect).toBeInTheDocument()
      })

      it('should render creation mode filter with default option selected', async () => {
        // When
        renderOffers(props, store)

        // Then
        expect(screen.getByDisplayValue('Tous les modes')).toBeInTheDocument()
      })

      it('should render creation mode filter with given creation mode selected', async () => {
        // Given
        const filters = { creation: 'importee' }

        // When
        renderOffers(props, store, filters)

        // Then
        expect(screen.getByDisplayValue('Importée')).toBeInTheDocument()
      })

      it('should allow user to select manual creation mode filter', () => {
        // Given
        renderOffers(props, store)
        const creationModeSelect = screen.getByDisplayValue('Tous les modes')

        // When
        fireEvent.change(creationModeSelect, { target: { value: 'manual' } })

        // Then
        expect(screen.getByDisplayValue('Manuelle')).toBeInTheDocument()
      })

      it('should allow user to select imported creation mode filter', () => {
        // Given
        renderOffers(props, store)
        const creationModeSelect = screen.getByDisplayValue('Tous les modes')

        // When
        fireEvent.change(creationModeSelect, { target: { value: 'imported' } })

        // Then
        expect(screen.getByDisplayValue('Importée')).toBeInTheDocument()
      })

      it('should display event period filter with no default option', async () => {
        // When
        await renderOffers(props, store)

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

        it('should filter offers given status filter when clicking on "Appliquer"', async () => {
          // Given
          renderOffers(props, store)
          fireEvent.click(
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )
          fireEvent.click(screen.getByLabelText('Expirée'))

          // When
          fireEvent.click(screen.getByText('Appliquer'))

          // Then
          expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
            creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
            nameOrIsbn: '',
            offererId: DEFAULT_SEARCH_FILTERS.offererId,
            venueId: DEFAULT_SEARCH_FILTERS.venueId,
            categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
            periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
            periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
            status: 'EXPIRED',
          })
        })

        it('should hide status filters when clicking outside the modal', async () => {
          // Given
          renderOffers(props, store)
          fireEvent.click(
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )

          // When
          fireEvent.click(
            screen.getByRole('heading', {
              name: 'Rechercher une offre',
              level: 3,
            })
          )

          // Then
          expect(screen.queryByText('Afficher les statuts')).toBeNull()
        })

        it('should indicate that no offers match selected filters', async () => {
          // Given
          pcapi.loadFilteredOffers
            .mockResolvedValueOnce(offersRecap)
            .mockResolvedValueOnce([])
          renderOffers(props, store)

          // When
          fireEvent.click(
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )
          fireEvent.click(screen.getByLabelText('Expirée'))
          fireEvent.click(screen.getByText('Appliquer'))

          // Then
          const noOffersForSearchFiltersText = await screen.findByText(
            'Aucune offre trouvée pour votre recherche'
          )
          expect(noOffersForSearchFiltersText).toBeInTheDocument()
        })

        it('should indicate that user has no offers yet', async () => {
          // Given
          pcapi.loadFilteredOffers.mockResolvedValue([])

          // When
          await renderOffers(props, store)

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
            const filters = { lieu: 'JI' }
            renderOffers(props, store, filters)

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

          it('should reset and disable status filter when venue filter is deselected', async () => {
            // Given
            const { id: venueId, name: venueName } = proVenues[0]
            const filters = {
              lieu: venueId,
              statut: 'inactive',
            }
            await renderOffers(props, store, filters)
            fireEvent.change(screen.getByDisplayValue(venueName), {
              target: { value: ALL_VENUES },
            })

            // When
            await fireEvent.click(screen.getByText('Lancer la recherche'))

            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
            expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
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

          it('should not reset or disable status filter when venue filter is deselected while offerer filter is applied', async () => {
            // Given
            const { id: venueId, name: venueName } = proVenues[0]
            const filters = {
              lieu: venueId,
              statut: 'inactive',
              structure: 'EF',
            }
            await renderOffers(props, store, filters)
            fireEvent.change(screen.getByDisplayValue(venueName), {
              target: { value: ALL_VENUES },
            })

            // When
            await fireEvent.click(screen.getByText('Lancer la recherche'))

            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
            expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
              nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
              venueId: DEFAULT_SEARCH_FILTERS.venueId,
              categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
              offererId: 'EF',
              status: 'INACTIVE',
              creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
              periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
              periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
            })
          })

          it('should reset and disable status filter when offerer filter is removed', async () => {
            // Given
            const offerer = { name: 'La structure', id: 'EF' }
            props.getOfferer.mockResolvedValueOnce(offerer)
            const filters = {
              structure: offerer.id,
              statut: 'inactive',
            }
            await renderOffers(props, store, filters)

            // When
            await fireEvent.click(
              screen.getByAltText('Supprimer le filtre par structure')
            )

            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
            expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
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

          it('should not reset or disable status filter when offerer filter is removed while venue filter is applied', async () => {
            // Given
            const { id: venueId } = proVenues[0]
            const offerer = { name: 'La structure', id: 'EF' }
            props.getOfferer.mockResolvedValueOnce(offerer)
            const filters = {
              lieu: venueId,
              statut: 'inactive',
              structure: offerer.id,
            }
            await renderOffers(props, store, filters)

            // When
            await fireEvent.click(
              screen.getByAltText('Supprimer le filtre par structure')
            )

            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
            expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
              nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
              venueId: venueId,
              categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
              offererId: DEFAULT_SEARCH_FILTERS.offererId,
              status: 'INACTIVE',
              creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
              periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
              periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
            })
          })

          it('should enable status filters when venue is selected but filter is not applied', async () => {
            // Given
            renderOffers(props, store)
            const venueOptionToSelect = await screen.findByRole('option', {
              name: proVenues[0].name,
            })

            // When
            userEvent.selectOptions(
              screen.getByLabelText('Lieu'),
              venueOptionToSelect
            )

            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })

          it('should enable status filters when venue filter is applied', async () => {
            // Given
            const filters = { lieu: 'IJ' }

            // When
            renderOffers(props, store, filters)

            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })

          it('should enable status filters when offerer filter is applied', async () => {
            // Given
            const filters = { structure: 'A4' }

            // When
            renderOffers(props, store, filters)

            // Then
            const statusFiltersIcon = await screen.findByAltText(
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
            const filters = { lieu: 'JI' }
            renderOffers(props, store, filters)

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
            // Given
            const filters = { lieu: 'IJ' }

            // When
            renderOffers(props, store, filters)

            // Then
            const selectAllOffersCheckbox = await screen.findByLabelText(
              'Tout sélectionner'
            )
            expect(selectAllOffersCheckbox).not.toBeDisabled()
          })

          it('should enable select all checkbox when offerer filter is applied', async () => {
            // Given
            const filters = { structure: 'A4' }
            // When
            renderOffers(props, store, filters)

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
        pcapi.loadFilteredOffers.mockResolvedValue(offers)

        // When
        renderOffers(props, store)

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
      await renderOffers(props, store)

      // When
      await fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
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

    it('should load offers with written offer name filter', async () => {
      // Given
      renderOffers(props, store)
      fireEvent.change(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par ISBN'),
        {
          target: { value: 'Any word' },
        }
      )

      // When
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
        nameOrIsbn: 'Any word',
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    })

    it('should load offers with selected venue filter', async () => {
      // Given
      await renderOffers(props, store)
      const firstVenueOption = await screen.findByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')
      userEvent.selectOptions(venueSelect, firstVenueOption)

      // When
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
        venueId: proVenues[0].id,
        nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    })

    it('should load offers with selected type filter', async () => {
      // Given
      await renderOffers(props, store)
      const firstTypeOption = await screen.findByRole('option', {
        name: 'Cinéma',
      })
      const typeSelect = screen.getByDisplayValue(
        ALL_CATEGORIES_OPTION.displayName,
        {
          selector: 'select[name="type"]',
        }
      )
      userEvent.selectOptions(typeSelect, firstTypeOption)

      // When
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        categoryId: 'CINEMA',
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    })

    it('should load offers with selected creation mode filter', () => {
      // Given
      renderOffers(props, store)
      const creationModeSelect = screen.getByDisplayValue(
        DEFAULT_CREATION_MODE.displayName
      )
      const importedCreationMode = CREATION_MODES_FILTERS[1].id
      fireEvent.change(creationModeSelect, {
        target: { value: importedCreationMode },
      })

      // When
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
        creationMode: 'imported',
        nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    })

    it('should load offers with selected period beginning date', async () => {
      // Given
      await renderOffers(props, store)

      fireEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[0])
      fireEvent.click(screen.getByText('25'))

      // When
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: '2020-12-25T00:00:00Z',
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    })

    it('should load offers with selected period ending date', async () => {
      // Given
      await renderOffers(props, store)

      fireEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[1])
      fireEvent.click(screen.getByText('27'))

      // When
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenLastCalledWith({
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        nameOrIsbn: DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: '2020-12-27T23:59:59Z',
      })
    })
  })

  describe('on click on event filter ending date', () => {
    it('should properly format received date', async () => {
      // Given
      renderOffers(props, store)
      fireEvent.change(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par ISBN'),
        {
          target: { value: 'Any word' },
        }
      )

      // When
      await fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
        nameOrIsbn: 'Any word',
        venueId: DEFAULT_SEARCH_FILTERS.venueId,
        categoryId: DEFAULT_SEARCH_FILTERS.categoryId,
        offererId: DEFAULT_SEARCH_FILTERS.offererId,
        status: DEFAULT_SEARCH_FILTERS.status,
        creationMode: DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate: DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate: DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    })

    it('should set new date value on filters', async () => {
      // Given
      renderOffers(props, store)
      fireEvent.change(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par ISBN'),
        {
          target: { value: 'Any word' },
        }
      )

      // When
      await fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
        nameOrIsbn: 'Any word',
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

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      // Given
      offersRecap = Array.from({ length: 11 }, offerFactory)
      pcapi.loadFilteredOffers.mockResolvedValueOnce(offersRecap)
      const { history } = renderOffers(props, store)
      const nextPageIcon = await screen.findByAltText(
        'Aller à la page suivante'
      )

      // When
      fireEvent.click(nextPageIcon)
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        page: '2',
      })
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      // Given
      const { history } = await renderOffers(props, store)

      // When
      fireEvent.change(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par ISBN'),
        {
          target: { value: 'AnyWord' },
        }
      )
      await fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({
        'nom-ou-isbn': 'AnyWord',
      })
    })

    it('should store search value', async () => {
      // Given
      await renderOffers(props, store)
      const searchInput = screen.getByPlaceholderText(
        'Rechercher par nom d’offre ou par ISBN'
      )

      // When
      fireEvent.change(searchInput, { target: { value: 'search string' } })
      await fireEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledWith({
        venueId: ALL_VENUES,
        categoryId: ALL_CATEGORIES,
        nameOrIsbn: 'search string',
        offererId: ALL_OFFERERS,
        status: ALL_STATUS,
        creationMode: DEFAULT_CREATION_MODE.id,
        periodBeginningDate: ALL_EVENT_PERIODS,
        periodEndingDate: ALL_EVENT_PERIODS,
      })
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      // Given
      const { history } = await renderOffers(props, store)

      // When
      fireEvent.change(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par ISBN'),
        {
          target: { value: ALL_OFFERS },
        }
      )
      await fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({})
    })

    it('should have venue value when user filters by venue', async () => {
      // Given
      const { history } = await renderOffers(props, store)
      const firstVenueOption = await screen.findByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')

      // When
      userEvent.selectOptions(venueSelect, firstVenueOption)
      await fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({
        lieu: proVenues[0].id,
      })
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      pcapi.loadCategories.mockResolvedValue({
        categories: [
          { id: 'test_id_1', proLabel: 'My test value', isSelectable: true },
          {
            id: 'test_id_2',
            proLabel: 'My second test value',
            isSelectable: true,
          },
        ],
      })

      const { history } = await renderOffers(props, store)
      const firstTypeOption = await screen.findByRole('option', {
        name: 'My test value',
      })
      const typeSelect = screen.getByDisplayValue(
        ALL_CATEGORIES_OPTION.displayName,
        {
          selector: 'select[name="categorie"]',
        }
      )

      // When
      userEvent.selectOptions(typeSelect, firstTypeOption)
      await fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({
        categorie: 'test_id_1',
      })
    })

    it('should have status value when user filters by status', async () => {
      // Given
      props.offers = [
        { id: 'KE', availabilityMessage: 'Pas de stock', status: 'ACTIVE' },
      ]
      const { history } = renderOffers(props, store)
      fireEvent.click(
        await screen.findByAltText('Afficher ou masquer le filtre par statut')
      )
      fireEvent.click(screen.getByLabelText('Épuisée'))

      // When
      await fireEvent.click(screen.getByText('Appliquer'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({
        statut: 'epuisee',
      })
    })

    it('should have status value be removed when user ask for all status', async () => {
      // Given
      props.offers = [
        { id: 'KE', availabilityMessage: 'Pas de stock', status: 'ACTIVE' },
      ]
      const { history } = await renderOffers(props, store)
      fireEvent.click(
        await screen.findByAltText('Afficher ou masquer le filtre par statut')
      )
      fireEvent.click(screen.getByLabelText('Tous'))

      // When
      fireEvent.click(screen.getByText('Appliquer'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({})
    })

    it('should have offerer filter when user filters by offerer', async () => {
      // Given
      const filters = { structure: 'A4' }
      props.getOfferer.mockResolvedValueOnce({ name: 'La structure' })

      // When
      renderOffers(props, store, filters)

      // Then
      const offererFilter = await screen.findByText('La structure')
      expect(offererFilter).toBeInTheDocument()
    })

    it('should have offerer value be removed when user removes offerer filter', async () => {
      // Given
      const filters = { structure: 'A4' }
      props.getOfferer.mockResolvedValueOnce({ name: 'La structure' })
      await renderOffers(props, store, filters)

      // When
      await fireEvent.click(
        screen.getByAltText('Supprimer le filtre par structure')
      )

      // Then
      expect(screen.queryByText('La structure')).not.toBeInTheDocument()
    })

    it('should have creation mode value when user filters by creation mode', async () => {
      // Given
      const { history } = renderOffers(props, store)

      // When
      fireEvent.change(screen.getByDisplayValue('Tous les modes'), {
        target: { value: 'manual' },
      })
      await fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({
        creation: 'manuelle',
      })
    })

    it('should have creation mode value be removed when user ask for all creation modes', async () => {
      // Given
      const { history } = renderOffers(props, store)
      const searchButton = screen.getByText('Lancer la recherche')
      fireEvent.change(screen.getByDisplayValue('Tous les modes'), {
        target: { value: 'manual' },
      })
      fireEvent.click(searchButton)

      // When
      fireEvent.change(screen.getByDisplayValue('Manuelle'), {
        target: { value: DEFAULT_CREATION_MODE.id },
      })
      await fireEvent.click(searchButton)
      const urlSearchParams = parse(history.location.search.substring(1))

      // Then
      expect(urlSearchParams).toMatchObject({})
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, offerFactory)
      pcapi.loadFilteredOffers.mockResolvedValueOnce(offers)
      renderOffers(props, store)
      const nextIcon = await screen.findByAltText('Aller à la page suivante')

      // When
      await fireEvent.click(nextIcon)

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(1)
      await expect(
        screen.findByText(offers[10].name)
      ).resolves.toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, offerFactory)
      pcapi.loadFilteredOffers.mockResolvedValueOnce(offers)
      renderOffers(props, store)
      const nextIcon = await screen.findByAltText('Aller à la page suivante')
      const previousIcon = await screen.findByAltText(
        'Aller à la page précédente'
      )
      await fireEvent.click(nextIcon)

      // When
      await fireEvent.click(previousIcon)

      // Then
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(1)
      await expect(
        screen.findByText(offers[0].name)
      ).resolves.toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    it('should not be able to click on previous arrow when being on the first page', async () => {
      // Given
      const filters = { page: DEFAULT_PAGE }
      const route = computeOffersUrl(filters)

      // When
      renderOffers(props, store, route)

      // Then
      const previousIcon = await screen.findByAltText(
        'Aller à la page précédente'
      )
      expect(previousIcon.closest('button')).toBeDisabled()
    })

    it('should not be able to click on next arrow when being on the last page', async () => {
      // Given
      pcapi.loadFilteredOffers.mockResolvedValueOnce(offersRecap)

      // When
      renderOffers(props, store)

      // Then
      const nextIcon = await screen.findByAltText('Aller à la page suivante')
      expect(nextIcon.closest('button')).toBeDisabled()
    })

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, offerFactory)
      })

      it('should have max number page of 50', async () => {
        // Given
        pcapi.loadFilteredOffers.mockResolvedValueOnce(offersRecap)

        // When
        renderOffers(props, store)

        // Then
        await expect(
          screen.findByText('Page 1/50')
        ).resolves.toBeInTheDocument()
      })

      it('should not display the 501st offer', async () => {
        // Given
        pcapi.loadFilteredOffers.mockResolvedValueOnce(offersRecap)
        renderOffers(props, store)
        const nextIcon = await screen.findByAltText('Aller à la page suivante')

        // When
        for (let i = 1; i < 51; i++) {
          fireEvent.click(nextIcon)
        }

        // Then
        expect(screen.getByText(offersRecap[499].name)).toBeInTheDocument()
        expect(
          screen.queryByText(offersRecap[500].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('offers selection', () => {
    it('should display actionsBar when at least one offer is selected', async () => {
      // Given
      renderWithStyles(
        <Provider store={store}>
          <MemoryRouter>
            <Offers {...props} />
          </MemoryRouter>
        </Provider>,
        {
          stylesheet: 'components/layout/ActionsBarPortal/_ActionsBarPortal',
        }
      )

      const actionBar = await screen.findByTestId('actions-bar')
      expect(actionBar).not.toBeVisible()

      // When
      const checkbox = await screen.findByTestId(
        `select-offer-${offersRecap[0].id}`
      )
      await fireEvent.click(checkbox)

      // Then
      expect(actionBar).toBeVisible()

      // When
      await fireEvent.click(checkbox)

      // Then
      expect(actionBar).not.toBeVisible()
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
        pcapi.loadFilteredOffers.mockResolvedValue(offers)
        pcapi.loadFilteredOffers.mockResolvedValue(offers)

        renderOffers(props, store)

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

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      pcapi.loadFilteredOffers
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      await renderOffers(props, store)
      const firstVenueOption = await screen.findByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName,
        {
          selector: 'select[name="lieu"]',
        }
      )
      userEvent.selectOptions(venueSelect, firstVenueOption)

      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(1)
      expect(pcapi.loadFilteredOffers).toHaveBeenNthCalledWith(1, {
        ...DEFAULT_SEARCH_FILTERS,
      })

      props.offers = []
      fireEvent.click(screen.getByText('Lancer la recherche'))
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(2)
      expect(pcapi.loadFilteredOffers).toHaveBeenNthCalledWith(2, {
        ...DEFAULT_SEARCH_FILTERS,
        venueId: proVenues[0].id,
      })

      await screen.findByText('Aucune offre trouvée pour votre recherche')
      fireEvent.click(screen.getByText('afficher toutes les offres'))
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(3)
      expect(pcapi.loadFilteredOffers).toHaveBeenNthCalledWith(3, {
        ...DEFAULT_SEARCH_FILTERS,
      })
    })

    it('when clicking on "Réinitialiser les filtres"', async () => {
      pcapi.loadFilteredOffers
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      await renderOffers(props, store)
      const venueOptionToSelect = await screen.findByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName,
        {
          selector: 'select[name="lieu"]',
        }
      )
      userEvent.selectOptions(venueSelect, venueOptionToSelect)

      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(1)
      expect(pcapi.loadFilteredOffers).toHaveBeenNthCalledWith(1, {
        ...DEFAULT_SEARCH_FILTERS,
      })

      props.offers = []
      fireEvent.click(screen.getByText('Lancer la recherche'))
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(2)
      expect(pcapi.loadFilteredOffers).toHaveBeenNthCalledWith(2, {
        ...DEFAULT_SEARCH_FILTERS,
        venueId: proVenues[0].id,
      })

      await fireEvent.click(screen.getByText('Réinitialiser les filtres'))
      expect(pcapi.loadFilteredOffers).toHaveBeenCalledTimes(3)
      expect(pcapi.loadFilteredOffers).toHaveBeenNthCalledWith(3, {
        ...DEFAULT_SEARCH_FILTERS,
      })
    })
  })
})
