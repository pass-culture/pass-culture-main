import { within } from '@testing-library/dom'
import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import NotificationV2Container from 'components/layout/NotificationV2/NotificationV2Container'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferLayoutContainer from '../../OfferLayoutContainer'
import { DEFAULT_FORM_VALUES } from '../OfferForm/_constants'

import {
  fieldLabels,
  findInputErrorForField,
  getOfferInputForField,
  queryInputErrorForField,
  setOfferValues,
} from './helpers'

jest.mock('repository/pcapi/pcapi', () => ({
  createOffer: jest.fn(),
  getValidatedOfferers: jest.fn(),
  getVenue: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadOffer: jest.fn(),
  loadStocks: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderOffers = async (props, store, queryParams = null) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{ pathname: '/offres/v2/creation', search: queryParams }]}>
          <Route path={['/offres/v2/creation', '/offres/v2/:offerId([A-Z0-9]+)']}>
            <>
              <OfferLayoutContainer {...props} />
              <NotificationV2Container />
            </>
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offerDetails - Creation - pro user', () => {
  let types
  let offerers
  let props
  let store
  let venues

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    props = {
      setShowThumbnailForm: jest.fn(),
    }
    types = [
      {
        conditionalFields: ['author', 'visa', 'stageDirector'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Cinéma - projections et autres évènements',
        type: 'Event',
        value: 'EventType.CINEMA',
      },
      {
        conditionalFields: ['author', 'musicType', 'performer', 'durationMinutes'],
        offlineOnly: false,
        onlineOnly: false,
        proLabel: 'Musique - concerts, festivals',
        type: 'Event',
        value: 'EventType.MUSIQUE',
      },
      {
        conditionalFields: ['author', 'showType', 'stageDirector', 'performer'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Spectacle vivant',
        type: 'Event',
        value: 'EventType.SPECTACLE_VIVANT',
      },
      {
        conditionalFields: [],
        offlineOnly: false,
        onlineOnly: true,
        proLabel: 'Presse en ligne - abonnements',
        type: 'Thing',
        value: 'ThingType.PRESSE_ABO',
      },
      {
        conditionalFields: ['author', 'isbn'],
        offlineOnly: false,
        onlineOnly: false,
        proLabel: 'Livres papier ou numérique, abonnements lecture',
        type: 'Thing',
        value: 'ThingType.LIVRE_EDITION',
      },
      {
        conditionalFields: [],
        offlineOnly: false,
        onlineOnly: true,
        proLabel: 'Cinéma - vente à distance',
        type: 'Thing',
        value: 'ThingType.CINEMA_CARD',
      },
      {
        conditionalFields: ['speaker'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Conférences, rencontres et découverte des métiers',
        type: 'Event',
        value: 'EventType.CONFERENCE_DEBAT_DEDICACE',
      },
    ]
    const offerer1Id = 'BA'
    const offerer2Id = 'BAC'
    offerers = [
      {
        id: offerer1Id,
        name: 'La structure',
      },
      {
        id: offerer2Id,
        name: "L'autre structure",
      },
    ]
    venues = [
      {
        id: 'AB',
        isVirtual: false,
        managingOffererId: offerer1Id,
        name: 'Le lieu',
        offererName: 'La structure',
      },
      {
        id: 'ABC',
        isVirtual: false,
        managingOffererId: offerer2Id,
        name: "L'autre lieu",
        offererName: "L'autre structure",
      },
      {
        id: 'ABCD',
        isVirtual: true,
        managingOffererId: offerer2Id,
        name: "L'autre lieu (Offre numérique)",
        offererName: "L'autre structure",
      },
    ]
    pcapi.loadTypes.mockResolvedValue(types)
    pcapi.getValidatedOfferers.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
    pcapi.getVenue.mockReturnValue(Promise.resolve())
    pcapi.createOffer.mockResolvedValue({})
    jest.spyOn(window, 'scrollTo').mockImplementation()
  })

  afterEach(() => {
    pcapi.createOffer.mockClear()
    pcapi.getValidatedOfferers.mockClear()
    pcapi.getVenuesForOfferer.mockClear()
    pcapi.loadTypes.mockClear()
  })

  describe('render when creating a new offer as pro user', () => {
    it('should get types from API', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(pcapi.loadTypes).toHaveBeenCalledTimes(1)
    })

    it("should get user's offerer from API", async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(pcapi.getValidatedOfferers).toHaveBeenCalledTimes(1)
    })

    it("should get user's venues from API", async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledTimes(1)
    })

    it('should have a section "Type d\'offre"', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(screen.getByText("Type d'offre", { selector: '.section-title' })).toBeInTheDocument()
    })

    it('should not display a placeholder for preview', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(
        screen.queryByText('Ajouter une image', { selector: 'button' })
      ).not.toBeInTheDocument()
    })

    describe('when selecting an offer type', () => {
      describe('when selecting physical type', () => {
        it('should inform user to add a venue if only virtual venue', async () => {
          // Given
          venues = [
            {
              id: 'AB',
              isVirtual: true,
              managingOffererId: 'AA',
              name: 'Le lieu (Offre Numérique)',
              offererName: 'Une structure',
            },
            {
              id: 'ABC',
              isVirtual: true,
              managingOffererId: 'AA',
              name: 'Un lieu (Offre Numérique)',
              offererName: 'Une structure',
            },
            {
              id: 'ABD',
              isVirtual: true,
              managingOffererId: 'AD',
              name: 'Un lieu (Offre Numérique)',
              offererName: 'Une autre structure',
            },
          ]
          pcapi.getVenuesForOfferer.mockResolvedValue(venues)
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })

          // Then
          expect(
            screen.getByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).toBeInTheDocument()
          expect(screen.getByRole('link', { name: '+ Ajouter un lieu' })).toHaveAttribute(
            'href',
            '/structures'
          )
          expect(screen.queryByLabelText('Type de spectacle')).not.toBeInTheDocument()
        })

        it('should not inform user about venue creation if at least one non virtual venue', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })

          // Then
          expect(
            screen.queryByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).not.toBeInTheDocument()
          expect(screen.queryByRole('link', { name: '+ Ajouter un lieu' })).not.toBeInTheDocument()
          expect(screen.getByLabelText('Type de spectacle')).toBeInTheDocument()
        })
      })

      describe('when selecting digital type', () => {
        it('should not inform user about venue creation if only virtual venue', async () => {
          // Given
          venues = [
            {
              id: 'AB',
              isVirtual: true,
              managingOffererId: 'AA',
              name: 'Le lieu (Offre Numérique)',
              offererName: 'Une structure',
            },
            {
              id: 'ABC',
              isVirtual: true,
              managingOffererId: 'AA',
              name: 'Un lieu (Offre Numérique)',
              offererName: 'Une structure',
            },
            {
              id: 'ABD',
              isVirtual: true,
              managingOffererId: 'AD',
              name: 'Un lieu (Offre Numérique)',
              offererName: 'Une autre structure',
            },
          ]
          pcapi.getVenuesForOfferer.mockResolvedValue(venues)
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'ThingType.CINEMA_CARD' })

          // Then
          expect(
            screen.queryByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).not.toBeInTheDocument()
          expect(screen.queryByRole('link', { name: '+ Ajouter un lieu' })).not.toBeInTheDocument()
        })
      })

      describe('when selecting physical or digital type', () => {
        it('should not inform user about venue creation if only virtual venue', async () => {
          // Given
          venues = [
            {
              id: 'AB',
              isVirtual: true,
              managingOffererId: 'AA',
              name: 'Le lieu (Offre Numérique)',
              offererName: 'Une structure',
            },
            {
              id: 'ABC',
              isVirtual: true,
              managingOffererId: 'AA',
              name: 'Un lieu (Offre Numérique)',
              offererName: 'Une structure',
            },
            {
              id: 'ABD',
              isVirtual: true,
              managingOffererId: 'AD',
              name: 'Un lieu (Offre Numérique)',
              offererName: 'Une autre structure',
            },
          ]
          pcapi.getVenuesForOfferer.mockResolvedValue(venues)
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })

          // Then
          expect(
            screen.queryByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).not.toBeInTheDocument()
          expect(screen.queryByRole('link', { name: '+ Ajouter un lieu' })).not.toBeInTheDocument()
        })
      })

      it('should display a placeholder for the offer thumbnail', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByText('Ajouter une image', { selector: 'button' })).toBeInTheDocument()
      })

      describe('offer preview', () => {
        it('should display title when input is filled', async () => {
          // given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // when
          const titleInput = await screen.findByLabelText("Titre de l'offre", { exact: false })
          userEvent.type(titleInput, 'Mon joli titre')

          // then
          expect(screen.getAllByText('Mon joli titre')).toHaveLength(2)
        })

        it('should display description when input is filled', async () => {
          // given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // when
          const descriptionInput = await screen.findByLabelText('Description', { exact: false })
          userEvent.type(descriptionInput, 'Ma jolie description')

          // then
          expect(await screen.queryAllByText('Ma jolie description')).toHaveLength(2)
        })

        it('should display terms of withdrawal when input is filled', async () => {
          // given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // when
          const withdrawalInput = await screen.findByLabelText('Informations de retrait', {
            exact: false,
          })
          userEvent.type(withdrawalInput, 'Mes jolies modalités')

          // then
          expect(await screen.queryAllByText('Mes jolies modalités')).toHaveLength(2)
        })

        it("should display disabled 'isDuo' icone for offers that aren't event", async () => {
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })
          const disabledisDuoBox = screen.queryByText('À deux !', {
            selector: '.op-option.disabled .op-option-text',
          })
          expect(disabledisDuoBox).toBeInTheDocument()
        })

        describe('"Où" section', () => {
          describe('when physical venue is selected', () => {
            it('should display "Où" section', async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              pcapi.getVenue.mockResolvedValue(physicalVenue)
              await setOfferValues({
                type: 'EventType.CINEMA',
                offererId: offererWithMultipleVenues.id,
              })

              // When
              userEvent.selectOptions(screen.getByLabelText('Lieu'), physicalVenue.id)

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(within(offerPreview).getByText('Où ?')).toBeInTheDocument()
              expect(within(offerPreview).getByText('Adresse')).toBeInTheDocument()
              expect(within(offerPreview).getByText('Distance')).toBeInTheDocument()
            })

            it("should display venue's public name if provided", async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              physicalVenue.publicName = 'Le petit nom du lieu'
              pcapi.getVenue.mockResolvedValue(physicalVenue)
              await setOfferValues({
                type: 'EventType.CINEMA',
                offererId: offererWithMultipleVenues.id,
              })

              // When
              userEvent.selectOptions(screen.getByLabelText('Lieu'), physicalVenue.id)

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(
                within(offerPreview).getByText(physicalVenue.publicName, { exact: false })
              ).toBeInTheDocument()
              expect(
                within(offerPreview).queryByText(physicalVenue.name, { exact: false })
              ).not.toBeInTheDocument()
            })

            it("should display venue's name if public name not provided", async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              pcapi.getVenue.mockResolvedValue(physicalVenue)
              await setOfferValues({
                type: 'EventType.CINEMA',
                offererId: offererWithMultipleVenues.id,
              })

              // When
              userEvent.selectOptions(screen.getByLabelText('Lieu'), physicalVenue.id)

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(
                within(offerPreview).getByText(physicalVenue.name, { exact: false })
              ).toBeInTheDocument()
            })

            it('should display formatted adress', async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              physicalVenue.address = "34 avenue de l'Opéra"
              physicalVenue.postalCode = '75002'
              physicalVenue.city = 'Paris'
              pcapi.getVenue.mockResolvedValue(physicalVenue)
              await setOfferValues({
                type: 'EventType.CINEMA',
                offererId: offererWithMultipleVenues.id,
              })

              // When
              userEvent.selectOptions(screen.getByLabelText('Lieu'), physicalVenue.id)

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              const expectedFormattedAddress = `${physicalVenue.name} - ${physicalVenue.address} - ${physicalVenue.postalCode} - ${physicalVenue.city}`
              expect(within(offerPreview).getByText(expectedFormattedAddress)).toBeInTheDocument()
            })
          })

          describe('when virtual venue is selected', () => {
            it('should not display "Où" section', async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const virtualVenue = venues[2]
              pcapi.getVenue.mockResolvedValue(virtualVenue)
              await setOfferValues({
                type: 'ThingType.CINEMA_CARD',
                offererId: offererWithMultipleVenues.id,
              })

              // When
              userEvent.selectOptions(screen.getByLabelText('Lieu'), virtualVenue.id)

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(within(offerPreview).queryByText('Où ?')).not.toBeInTheDocument()
              expect(within(offerPreview).queryByText('Adresse')).not.toBeInTheDocument()
              expect(within(offerPreview).queryByText('Distance')).not.toBeInTheDocument()
            })
          })

          describe('when no venue is selected', () => {
            it('should not display "Où" section', async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              await setOfferValues({
                type: 'EventType.CINEMA',
                offererId: offererWithMultipleVenues.id,
              })

              // When
              userEvent.selectOptions(screen.getByLabelText('Lieu'), physicalVenue.id)
              userEvent.selectOptions(screen.getByLabelText('Lieu'), '')

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(within(offerPreview).queryByText('Où ?')).not.toBeInTheDocument()
              expect(within(offerPreview).queryByText('Adresse')).not.toBeInTheDocument()
              expect(within(offerPreview).queryByText('Distance')).not.toBeInTheDocument()
            })
          })
        })
      })

      it('should display "Infos pratiques", "Infos artistiques", "Accessibilité", "Lien de réservation externe" and "Autre" section', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(
          screen.getByRole('heading', { name: 'Informations artistiques', level: 3 })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('heading', { name: 'Informations pratiques', level: 3 })
        ).toBeInTheDocument()
        expect(screen.getByRole('heading', { name: 'Accessibilité', level: 3 })).toBeInTheDocument()
        expect(
          screen.getByRole('heading', { name: 'Lien de réservation externe', level: 3 })
        ).toBeInTheDocument()
        expect(screen.getByRole('heading', { name: 'Autre', level: 3 })).toBeInTheDocument()
      })

      it('should display email notification input when asking to receive booking emails', async () => {
        // Given
        await renderOffers(props, store)
        await setOfferValues({ type: 'EventType.MUSIQUE' })

        // When
        await setOfferValues({ receiveNotificationEmails: true })

        // Then
        const bookingEmailInput = screen.getByLabelText('Email auquel envoyer les notifications :')
        expect(bookingEmailInput).toBeInTheDocument()
      })

      it('should display a text input for an external ticket office url"', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await setOfferValues({ type: 'EventType.MUSIQUE' })

        // Then
        const externalTicketOfficeUrlInput = await getOfferInputForField('externalTicketOfficeUrl')
        expect(externalTicketOfficeUrlInput).toBeInTheDocument()
      })

      describe('accessibility fields', () => {
        it('should display accessibility section description', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(
            screen.getByText(
              'Cette offre est-elle accessible aux publics en situation de handicaps :'
            )
          ).toBeInTheDocument()
        })

        it('should display accessibility checkboxes unchecked by default', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(
            screen.getByLabelText('Handicap visuel', { selector: 'input[type="checkbox"]' })
          ).not.toBeChecked()
          expect(
            screen.getByLabelText('Handicap mental', { selector: 'input[type="checkbox"]' })
          ).not.toBeChecked()
          expect(
            screen.getByLabelText('Handicap moteur', { selector: 'input[type="checkbox"]' })
          ).not.toBeChecked()
          expect(
            screen.getByLabelText('Handicap auditif', { selector: 'input[type="checkbox"]' })
          ).not.toBeChecked()
        })
      })

      describe('venue selection', () => {
        it('should display an offerer selection and a venue selection when user is pro', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.queryByLabelText('Structure')).toBeInTheDocument()
          const venueInput = screen.queryByLabelText('Lieu')
          expect(venueInput).toBeInTheDocument()
          expect(venueInput).not.toHaveAttribute('disabled')
        })

        it('should have offerer selected when given as queryParam and filter venues', async () => {
          // Given
          await renderOffers(props, store, `?structure=${offerers[0].id}`)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.queryByText(venues[1].name)).not.toBeInTheDocument()
          expect(screen.queryByText(venues[2].name)).not.toBeInTheDocument()
        })

        it('should select offerer when there is only one option', async () => {
          // Given
          pcapi.getValidatedOfferers.mockResolvedValue([offerers[0]])
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
        })

        it('should have venue selected when given as queryParam', async () => {
          // Given
          await renderOffers(
            props,
            store,
            `?lieu=${venues[0].id}&structure=${venues[0].managingOffererId}`
          )

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
        })

        it('should select venue when there is only one option', async () => {
          // Given
          pcapi.getVenuesForOfferer.mockResolvedValue([venues[0]])
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
        })

        it('should only display virtual venues when offer type is online only', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })

          // Then
          expect(screen.queryByText(venues[0].name)).not.toBeInTheDocument()
          expect(screen.queryByText(venues[1].name)).not.toBeInTheDocument()
          expect(screen.getByText(venues[2].name)).toBeInTheDocument()
        })

        it('should only display physical venues when offer type is offline only', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[1].name)).toBeInTheDocument()
          expect(screen.queryByText(venues[2].name)).not.toBeInTheDocument()
        })

        it('should display all venues when offer type is offline and online', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[1].name)).toBeInTheDocument()
          expect(screen.getByText(venues[2].name)).toBeInTheDocument()
        })

        it('should only display venues of selected offerer', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // When
          await setOfferValues({ offererId: offerers[0].id })

          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.queryByText(venues[1].name)).not.toBeInTheDocument()
          expect(screen.queryByText(venues[2].name)).not.toBeInTheDocument()
        })

        it('should display all venues when unselecting offerer', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.MUSIQUE' })
          await setOfferValues({ offererId: offerers[0].id })

          // When
          await setOfferValues({ offererId: '' })

          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[1].name)).toBeInTheDocument()
          expect(screen.getByText(venues[2].name)).toBeInTheDocument()
        })

        it('should select offerer of selected venue', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // When
          await setOfferValues({ venueId: venues[0].id })

          // Then
          expect(screen.getByLabelText('Structure')).toHaveDisplayValue(offerers[0].name)
        })

        it('should warn user if selected offerer has no physical venues but physical type is selected', async () => {
          // Given
          const venues = [
            {
              id: 'CCC',
              isVirtual: true,
              managingOffererId: offerers[0].id,
              name: 'Le lieu',
              offererName: 'La structure',
            },
            {
              id: 'DDD',
              isVirtual: false,
              managingOffererId: offerers[1].id,
              name: "L'autre lieu",
              offererName: "L'autre structure",
            },
            {
              id: 'EEE',
              isVirtual: true,
              managingOffererId: offerers[1].id,
              name: "L'autre lieu (Offre numérique)",
              offererName: "L'autre structure",
            },
          ]
          pcapi.getVenuesForOfferer.mockResolvedValue(venues)
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // When
          await setOfferValues({ offererId: offerers[0].id })

          // Then
          const venueInput = screen.getByLabelText('Lieu')
          expect(venueInput).toBeInTheDocument()
          expect(venueInput).not.toHaveAttribute('disabled')
          const venueIdError = await findInputErrorForField('venueId')
          expect(venueIdError).toHaveTextContent(
            'Il faut obligatoirement une structure avec un lieu.'
          )
        })

        it('should warn user if selected offerer has no physical venues but physical type is selected while coming from offerer page', async () => {
          // Given
          const venues = [
            {
              id: 'CCC',
              isVirtual: true,
              managingOffererId: offerers[0].id,
              name: 'Le lieu',
              offererName: 'La structure',
            },
            {
              id: 'DDD',
              isVirtual: false,
              managingOffererId: offerers[1].id,
              name: "L'autre lieu",
              offererName: "L'autre structure",
            },
            {
              id: 'EEE',
              isVirtual: true,
              managingOffererId: offerers[1].id,
              name: "L'autre lieu (Offre numérique)",
              offererName: "L'autre structure",
            },
          ]
          pcapi.getVenuesForOfferer.mockResolvedValue(venues)
          await renderOffers(props, store, `?structure=${offerers[1].id}`)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // When
          await setOfferValues({ offererId: offerers[0].id })

          // Then
          const venueInput = screen.getByLabelText('Lieu')
          expect(venueInput).toBeInTheDocument()
          expect(venueInput).not.toHaveAttribute('disabled')
          const venueIdError = await findInputErrorForField('venueId')
          expect(venueIdError).toHaveTextContent(
            'Il faut obligatoirement une structure avec un lieu.'
          )
        })

        it('should remove no physical venue warning when it is no longer valid', async () => {
          // Given
          pcapi.getVenuesForOfferer.mockResolvedValue([
            {
              id: 'AB',
              isVirtual: true,
              managingOffererId: offerers[0].id,
              name: 'Le lieu virtuel',
              offererName: 'La structure',
            },
          ])
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.CINEMA' })

          // When
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })

          // Then
          expect(screen.getByLabelText('Lieu')).toBeInTheDocument()
          const venueIdError = queryInputErrorForField('venueId')
          expect(venueIdError).toBeNull()
        })
      })

      describe('with conditional fields', () => {
        describe('"musicType"', () => {
          it('should display a music type selection', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.MUSIQUE' })

            // Then
            const musicTypeInput = await getOfferInputForField('musicType')
            expect(musicTypeInput).toBeInTheDocument()
          })

          it('should display a music subtype selection when a musicType is selected', async () => {
            // Given
            await renderOffers(props, store)
            await setOfferValues({ type: 'EventType.MUSIQUE' })

            // When
            await setOfferValues({ musicType: '501' })

            // Then
            const musicSubTypeInput = await getOfferInputForField('musicSubType')
            expect(musicSubTypeInput).toBeInTheDocument()
          })

          it('should not display a music type selection when changing to an offer type wihtout "musicType" conditional field', async () => {
            // Given
            await renderOffers(props, store)
            await setOfferValues({ type: 'EventType.MUSIQUE' })
            await screen.findByLabelText('Genre musical', { exact: false })

            // When
            await setOfferValues({ type: 'EventType.CINEMA' })

            // Then
            expect(
              screen.queryByLabelText('Genre musical', { exact: false })
            ).not.toBeInTheDocument()
          })

          it('should not display a music subtype selection when a musicType is not selected and a showType was selected before', async () => {
            // Given
            await renderOffers(props, store)
            await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })
            await setOfferValues({ showType: '1300' })
            await setOfferValues({ showSubType: '1307' })

            // When
            await setOfferValues({ type: 'EventType.MUSIQUE' })

            // Then
            expect(screen.queryByLabelText('Sous genre', { exact: false })).not.toBeInTheDocument()
          })
        })

        describe('"showType"', () => {
          it('should display a show type selection', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })

            // Then
            const showTypeInput = await getOfferInputForField('showType')
            expect(showTypeInput).toBeInTheDocument()
          })

          it('should display a show subtype selection when a showType is selected', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })
            await setOfferValues({ showType: '1300' })

            // Then
            const showSubTypeInput = await getOfferInputForField('showSubType')
            expect(showSubTypeInput).toBeInTheDocument()
          })
        })

        describe('"speaker"', () => {
          it('should display a text input "intervenant"', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.CONFERENCE_DEBAT_DEDICACE' })

            // Then
            const speakerInput = await getOfferInputForField('speaker')
            expect(speakerInput).toBeInTheDocument()
          })
        })

        describe('"author"', () => {
          it('should display a text input "auteur"', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.CINEMA' })

            // Then
            const authorInput = await getOfferInputForField('author')
            expect(authorInput).toBeInTheDocument()
          })
        })

        describe('"visa"', () => {
          it("should display a text input 'Visa d'exploitation'", async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.CINEMA' })

            // Then
            const visaInput = await getOfferInputForField('visa')
            expect(visaInput).toBeInTheDocument()
          })
        })

        describe('"isbn"', () => {
          it('should display a text input "ISBN"', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })

            // Then
            const isbnInput = await getOfferInputForField('isbn')
            expect(isbnInput).toBeInTheDocument()
          })
        })

        describe('"stageDirector"', () => {
          it('should display a text input "Metteur en scène"', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.CINEMA' })

            // Then
            const stageDirectorInput = await getOfferInputForField('stageDirector')
            expect(stageDirectorInput).toBeInTheDocument()
          })
        })

        describe('"performer"', () => {
          it('should display a text input "Interprète"', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ type: 'EventType.MUSIQUE' })

            // Then
            const performerInput = await getOfferInputForField('performer')
            expect(performerInput).toBeInTheDocument()
          })
        })
      })

      describe('when selecting a virtual venue', () => {
        it('should display a text input "url"', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })

          // When
          await setOfferValues({ venueId: venues[2].id })

          // Then
          const urlInput = await getOfferInputForField('url')
          expect(urlInput).toBeInTheDocument()
        })

        it('should display refundable banner when offer type is online only', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })

          // When
          await setOfferValues({ venueId: venues[2].id })

          // Then
          expect(
            screen.getByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).toBeInTheDocument()
        })

        it('should remove refundable banner after deselecting the venue', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })
          await setOfferValues({ venueId: venues[2].id })

          // When
          await setOfferValues({ venueId: DEFAULT_FORM_VALUES.venueId })

          // Then
          expect(
            screen.queryByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).not.toBeInTheDocument()
        })

        it('should remove refundable banner after selecting a refundable offer type', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })
          await setOfferValues({ venueId: venues[2].id })

          // When
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })

          // Then
          expect(
            screen.queryByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).not.toBeInTheDocument()
        })

        it('should display refundable banner when offer type is online and offline', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // When
          await setOfferValues({ venueId: venues[2].id })

          // Then
          expect(
            screen.getByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).toBeInTheDocument()
        })

        it('should not display refundable banner when offer type is ThingType.LIVRE_EDITION', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })

          // When
          await setOfferValues({ venueId: venues[2].id })

          // Then
          expect(
            screen.queryByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).not.toBeInTheDocument()
        })

        it('should not display refundable banner when offer type is ThingType.CINEMA_CARD', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.CINEMA_CARD' })

          // When
          await setOfferValues({ venueId: venues[2].id })

          // Then
          expect(
            screen.queryByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).not.toBeInTheDocument()
        })

        it('should not remind withdrawal modalities', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'ThingType.CINEMA_CARD' })

          // When
          await setOfferValues({ venueId: venues[2].id })

          // Then
          const withdrawalModalitiesReminder = screen.queryByText(
            "La livraison d'article n'est pas autorisée. Pour plus d'informations, veuillez consulter nos CGU."
          )
          expect(withdrawalModalitiesReminder).not.toBeInTheDocument()
        })
      })

      describe('when offer type is event type', () => {
        it('should display a time input "Durée"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const durationInput = await getOfferInputForField('durationMinutes')
          expect(durationInput).toBeInTheDocument()
        })

        it('should display a checkbox input "Offre duo" checked by default', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const duoInput = await getOfferInputForField('isDuo')
          expect(duoInput).toBeInTheDocument()
          expect(duoInput).toBeChecked()
        })

        it('should not remind withdrawal modalities', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const withdrawalModalitiesReminder = screen.queryByText(
            "La livraison d'article n'est pas autorisée. Pour plus d'informations, veuillez consulter nos CGU."
          )
          expect(withdrawalModalitiesReminder).not.toBeInTheDocument()
        })
      })

      describe('when offer type is thing type and venue is not virtual', () => {
        it('should remind withdrawal modalities in "Informations pratiques" section', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION', venueId: venues[0].id })

          // Then
          const informationsPratiquesSection = within(
            screen.getByText('Informations pratiques').closest('section')
          )
          const withdrawalModalitiesReminder = informationsPratiquesSection.getByText(
            "La livraison d'article n'est pas autorisée. Pour plus d'informations, veuillez consulter nos CGU."
          )
          expect(withdrawalModalitiesReminder).toBeInTheDocument()
        })
      })

      it('should initialize empty disabilityCompliance', async () => {
        // Given
        await renderOffers(props, store)
        await setOfferValues({ type: 'ThingType.LIVRE_EDITION', venueId: venues[0].id })

        // Then
        const audioDisabilityCompliantCheckbox = screen.getByLabelText(
          fieldLabels.audioDisabilityCompliant.label,
          {
            exact: fieldLabels.audioDisabilityCompliant.exact,
          }
        )
        expect(audioDisabilityCompliantCheckbox).not.toBeChecked()

        const mentalDisabilityCompliantCheckbox = screen.getByLabelText(
          fieldLabels.mentalDisabilityCompliant.label,
          {
            exact: fieldLabels.mentalDisabilityCompliant.exact,
          }
        )
        expect(mentalDisabilityCompliantCheckbox).not.toBeChecked()

        const motorDisabilityCompliantCheckbox = screen.getByLabelText(
          fieldLabels.motorDisabilityCompliant.label,
          {
            exact: fieldLabels.motorDisabilityCompliant.exact,
          }
        )
        expect(motorDisabilityCompliantCheckbox).not.toBeChecked()

        const visualDisabilityCompliantCheckbox = screen.getByLabelText(
          fieldLabels.visualDisabilityCompliant.label,
          {
            exact: fieldLabels.visualDisabilityCompliant.exact,
          }
        )
        expect(visualDisabilityCompliantCheckbox).not.toBeChecked()

        const noDisabilityCompliantCheckbox = screen.getByLabelText(
          fieldLabels.noDisabilityCompliant.label,
          {
            exact: fieldLabels.noDisabilityCompliant.exact,
          }
        )
        expect(noDisabilityCompliantCheckbox).not.toBeChecked()
      })
    })
  })

  describe('when submitting form', () => {
    beforeEach(() => {
      pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    })

    it('should call API with offer data', async () => {
      // Given
      const offerValues = {
        name: 'Ma petite offre',
        description: 'Pas si petite que ça',
        durationMinutes: '1:30',
        isDuo: false,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        externalTicketOfficeUrl: 'http://example.net',
        type: 'EventType.MUSIQUE',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        venueId: venues[0].id,
        withdrawalDetails: 'À venir chercher sur place.',
      }

      await renderOffers(props, store)

      await setOfferValues({ type: offerValues.type })
      await setOfferValues(offerValues)

      // When
      await userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      expect(pcapi.createOffer).toHaveBeenCalledWith({
        ...offerValues,
        bookingEmail: null,
        durationMinutes: 90,
      })
    })

    it('should submit externalTicketOfficeUrl as null when no value was provided', async () => {
      // Given
      const offerValues = {
        name: 'Ma petite offre',
        type: 'EventType.MUSIQUE',
        venueId: venues[0].id,
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      await renderOffers(props, store)

      await setOfferValues({ type: offerValues.type })
      await setOfferValues(offerValues)

      // When
      await userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      expect(pcapi.createOffer).toHaveBeenCalledWith(
        expect.objectContaining({
          externalTicketOfficeUrl: null,
        })
      )
    })

    it('should show a success notification and redirect to stock page when form was correctly submitted', async () => {
      // Given
      const offerValues = {
        name: 'Ma petite offre',
        description: 'Pas si petite que ça',
        durationMinutes: '1:30',
        type: 'EventType.MUSIQUE',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        venueId: venues[0].id,
        isDuo: false,
        withdrawalDetails: 'À venir chercher sur place.',
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      const createdOffer = { ...offerValues, id: 'CREATED', stocks: [], venue: venues[0] }
      pcapi.createOffer.mockResolvedValue(createdOffer)
      await renderOffers(props, store)
      pcapi.loadOffer.mockResolvedValue(createdOffer)

      await setOfferValues({ type: offerValues.type })
      await setOfferValues(offerValues)

      // When
      userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      const successNotification = await screen.findByText('Votre offre a bien été créée')
      expect(successNotification).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Nouvelle offre', level: 1 })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Stock et prix', level: 3 })).toBeInTheDocument()
    })

    it('should show errors for mandatory fields', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ type: 'EventType.MUSIQUE' })

      // When
      userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      expect(pcapi.createOffer).not.toHaveBeenCalled()

      // Mandatory fields
      const nameError = await findInputErrorForField('name')
      expect(nameError).toHaveTextContent('Ce champ est obligatoire')
      const venueIdError = await findInputErrorForField('venueId')
      expect(venueIdError).toHaveTextContent('Ce champ est obligatoire')
      const offererIdError = await findInputErrorForField('offererId')
      expect(offererIdError).toHaveTextContent('Ce champ est obligatoire')

      // Optional fields
      const descriptionError = queryInputErrorForField('description')
      expect(descriptionError).toBeNull()
      const durationMinutesError = queryInputErrorForField('durationMinutes')
      expect(durationMinutesError).toBeNull()
      const typeError = queryInputErrorForField('type')
      expect(typeError).toBeNull()
      const authorError = queryInputErrorForField('author')
      expect(authorError).toBeNull()
      const musicTypeError = queryInputErrorForField('musicType')
      expect(musicTypeError).toBeNull()
      const musicSubTypeError = queryInputErrorForField('musicSubType')
      expect(musicSubTypeError).toBeNull()
      const performerError = queryInputErrorForField('performer')
      expect(performerError).toBeNull()
      const isDuoError = queryInputErrorForField('isDuo')
      expect(isDuoError).toBeNull()
      const withdrawalDetailsError = queryInputErrorForField('withdrawalDetails')
      expect(withdrawalDetailsError).toBeNull()
      const bookingEmailInput = queryInputErrorForField('bookingEmail')
      expect(bookingEmailInput).toBeNull()
    })

    it('should show an error notification when form is not valid', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ type: 'EventType.MUSIQUE' })

      // When
      userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      const errorNotification = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
      expect(errorNotification).toBeInTheDocument()
    })

    it('should show error for email notification input when asking to receive booking emails and no email was provided', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ type: 'EventType.MUSIQUE' })
      await setOfferValues({ receiveNotificationEmails: true })

      // When
      userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      const bookingEmailInput = await findInputErrorForField('bookingEmail')
      expect(bookingEmailInput).toHaveTextContent('Ce champ est obligatoire')
    })

    it('should show error sent by API and show an error notification', async () => {
      // Given
      const offerValues = {
        name: 'Ce nom serait-il invalide ?',
        description: 'Pas si petite que ça',
        durationMinutes: '1:30',
        type: 'EventType.MUSIQUE',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        venueId: venues[0].id,
        isDuo: false,
        withdrawalDetails: 'À venir chercher sur place.',
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      pcapi.createOffer.mockRejectedValue({ errors: { name: "Ce nom n'est pas valide" } })
      await renderOffers(props, store)

      await setOfferValues({ type: offerValues.type })
      await setOfferValues(offerValues)

      // When
      userEvent.click(screen.getByText('Enregistrer et passer aux stocks'))

      // Then
      const nameError = await screen.findByText("Ce nom n'est pas valide")
      expect(nameError).toBeInTheDocument()
      const errorNotification = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
      expect(errorNotification).toBeInTheDocument()
    })
  })
})
