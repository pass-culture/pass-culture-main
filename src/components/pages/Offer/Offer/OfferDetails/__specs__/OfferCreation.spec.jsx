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
  findInputErrorForField,
  getOfferInputForField,
  queryInputErrorForField,
  setOfferValues,
} from './helpers'

jest.mock('repository/pcapi/pcapi', () => ({
  createOffer: jest.fn(),
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderOffers = async (props, store, queryParams = null) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{ pathname: '/offres/v2/creation', search: queryParams }]}>
          <Route path="/offres/v2/">
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

describe('offerDetails - Creation', () => {
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
    offerers = [
      {
        id: 'BA',
        name: 'La structure',
      },
      {
        id: 'BAC',
        name: "L'autre structure",
      },
    ]
    venues = [
      {
        id: 'AB',
        isVirtual: false,
        managingOffererId: offerers[0].id,
        name: 'Le lieu',
        offererName: 'La structure',
      },
      {
        id: 'ABC',
        isVirtual: false,
        managingOffererId: offerers[1].id,
        name: "L'autre lieu",
        offererName: "L'autre structure",
      },
      {
        id: 'ABCD',
        isVirtual: true,
        managingOffererId: offerers[1].id,
        name: "L'autre lieu (Offre numérique)",
        offererName: "L'autre structure",
      },
    ]
    pcapi.loadTypes.mockResolvedValue(types)
    pcapi.getValidatedOfferers.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockImplementation(offererId =>
      Promise.resolve(
        venues.filter(venue => (offererId ? venue.managingOffererId === offererId : true))
      )
    )
    jest.spyOn(window, 'scrollTo').mockImplementation()
  })

  afterEach(() => {
    pcapi.createOffer.mockClear()
    pcapi.getValidatedOfferers.mockClear()
    pcapi.getVenuesForOfferer.mockClear()
    pcapi.loadTypes.mockClear()
  })

  describe('render when creating a new offer', () => {
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
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledWith(null)
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
      it('should display a placeholder for preview', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByText('Ajouter une image', { selector: 'button' })).toBeInTheDocument()
      })

      it('should display "Infos pratiques", "Infos artistiques", and "Autre" section', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(
          screen.getByText('Infos artistiques', { selector: '.section-title' })
        ).toBeInTheDocument()
        expect(
          screen.getByText('Informations pratiques', { selector: '.section-title' })
        ).toBeInTheDocument()
        expect(screen.getByText('Autre', { selector: '.section-title' })).toBeInTheDocument()
      })

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

      it('should have offerer selected when given as queryParam', async () => {
        // Given
        await renderOffers(props, store, `?structure=${offerers[0].id}`)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
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
        expect(pcapi.getVenuesForOfferer).toHaveBeenCalledWith(offerers[0].id)
      })

      it('should warn user that his offerer has no physical venues when selecting a physical offer and no venues are physical', async () => {
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

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

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

      it('should select offerer of selected venue', async () => {
        // Given
        await renderOffers(props, store)
        await setOfferValues({ type: 'EventType.CINEMA' })

        // When
        await setOfferValues({ venueId: venues[0].id })

        // Then
        expect(screen.getByLabelText('Structure')).toHaveDisplayValue(offerers[0].name)
      })

      it('should display email notification input when asking to receive booking emails', async () => {
        // Given
        await renderOffers(props, store)
        await setOfferValues({ type: 'EventType.MUSIQUE' })

        // When
        await setOfferValues({ receiveNotificationEmails: true })

        // Then
        const bookingEmailInput = screen.getByLabelText(
          'Être notifié par email des réservations à :'
        )
        expect(bookingEmailInput).toBeInTheDocument()
        expect(bookingEmailInput).toHaveAttribute('name', 'bookingEmail')
      })

      describe('with conditional field "musicType"', () => {
        it('should display a music type selection', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const musicTypeInput = await getOfferInputForField('musicType')
          expect(musicTypeInput).toBeInTheDocument()
          expect(musicTypeInput).toHaveAttribute('name', 'musicType')
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
          expect(musicSubTypeInput).toHaveAttribute('name', 'musicSubType')
        })

        it('should not display a music type selection when changing to an offer type wihtout "musicType" conditional field', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ type: 'EventType.MUSIQUE' })
          await screen.findByLabelText('Genre musical', { exact: false })

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.queryByLabelText('Genre musical', { exact: false })).not.toBeInTheDocument()
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

      describe('with conditional field "showType"', () => {
        it('should display a show type selection', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })

          // Then
          const showTypeInput = await getOfferInputForField('showType')
          expect(showTypeInput).toBeInTheDocument()
          expect(showTypeInput).toHaveAttribute('name', 'showType')
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
          expect(showSubTypeInput).toHaveAttribute('name', 'showSubType')
        })
      })

      describe('with conditional field "speaker"', () => {
        it('should display a text input "intervenant"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CONFERENCE_DEBAT_DEDICACE' })

          // Then
          const speakerInput = await getOfferInputForField('speaker')
          expect(speakerInput).toBeInTheDocument()
          expect(speakerInput).toHaveAttribute('name', 'speaker')
        })
      })

      describe('with conditional field "author"', () => {
        it('should display a text input "auteur"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          const authorInput = await getOfferInputForField('author')
          expect(authorInput).toBeInTheDocument()
          expect(authorInput).toHaveAttribute('name', 'author')
        })
      })

      describe('with conditional field "visa"', () => {
        it("should display a text input 'Visa d'exploitation'", async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          const visaInput = await getOfferInputForField('visa')
          expect(visaInput).toBeInTheDocument()
          expect(visaInput).toHaveAttribute('name', 'visa')
        })
      })

      describe('with conditional field "isbn"', () => {
        it('should display a text input "ISBN"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })

          // Then
          const isbnInput = await getOfferInputForField('isbn')
          expect(isbnInput).toBeInTheDocument()
          expect(isbnInput).toHaveAttribute('name', 'isbn')
        })
      })

      describe('with conditional field "stageDirector"', () => {
        it('should display a text input "Metteur en scène"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          const stageDirectorInput = await getOfferInputForField('stageDirector')
          expect(stageDirectorInput).toBeInTheDocument()
          expect(stageDirectorInput).toHaveAttribute('name', 'stageDirector')
        })
      })

      describe('with conditional field "performer"', () => {
        it('should display a text input "Interprète"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const performerInput = await getOfferInputForField('performer')
          expect(performerInput).toHaveAttribute('name', 'performer')
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
          expect(urlInput).toHaveAttribute('name', 'url')
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
          expect(durationInput).toHaveAttribute('name', 'durationMinutes')
        })

        it('should display a checkbox input "Offre duo" checked by default', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const duoInput = await getOfferInputForField('isDuo')
          expect(duoInput).toBeInTheDocument()
          expect(duoInput).toHaveAttribute('name', 'isDuo')
          expect(duoInput).toBeChecked()
        })
      })
    })
  })

  describe('when submitting form', () => {
    it('should call API with offer data', async () => {
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
      }

      await renderOffers(props, store)

      await setOfferValues({ type: offerValues.type })
      await setOfferValues(offerValues)

      // When
      userEvent.click(screen.getByText('Enregistrer et passer au stocks'))

      // Then
      expect(pcapi.createOffer).toHaveBeenCalledWith({
        ...offerValues,
        bookingEmail: null,
        durationMinutes: 90,
      })
    })
  })

  it('should show errors for mandatory fields', async () => {
    // Given
    await renderOffers(props, store)
    await setOfferValues({ type: 'EventType.MUSIQUE' })

    // When
    userEvent.click(screen.getByText('Enregistrer et passer au stocks'))

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
    userEvent.click(screen.getByText('Enregistrer et passer au stocks'))

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
    userEvent.click(screen.getByText('Enregistrer et passer au stocks'))

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
    }

    pcapi.createOffer.mockRejectedValue({ errors: { name: "Ce nom n'est pas valide" } })
    await renderOffers(props, store)

    await setOfferValues({ type: offerValues.type })
    await setOfferValues(offerValues)

    // When
    userEvent.click(screen.getByText('Enregistrer et passer au stocks'))

    // Then
    const nameError = await screen.findByText("Ce nom n'est pas valide")
    expect(nameError).toBeInTheDocument()
    const errorNotification = await screen.findByText(
      'Une ou plusieurs erreurs sont présentes dans le formulaire'
    )
    expect(errorNotification).toBeInTheDocument()
  })
})
