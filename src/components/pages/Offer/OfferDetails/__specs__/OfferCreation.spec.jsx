import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferDetailsContainer from '../OfferDetailsContainer'

import { setOfferValues } from './helpers'

jest.mock('repository/pcapi/pcapi', () => ({
  createOffer: jest.fn(),
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderOffers = (props, store, queryParams = null) => {
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[{ pathname: '/offres/v2/creation', search: queryParams }]}>
        <OfferDetailsContainer {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('offerDetails - Creation', () => {
  let types
  let offerers
  let store
  let venues

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
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
        conditionalFields: ['author', 'musicType', 'performer'],
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
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
  })

  afterEach(() => {
    pcapi.loadTypes.mockClear()
    pcapi.getValidatedOfferers.mockClear()
    pcapi.getVenuesForOfferer.mockClear()
  })

  describe('render when creating a new offer', () => {
    it('should get types from API', async () => {
      // When
      renderOffers({}, store)

      // Then
      expect(pcapi.loadTypes).toHaveBeenCalledTimes(1)
    })

    it("should get user's offerer from API", async () => {
      // When
      renderOffers({}, store)

      // Then
      expect(pcapi.getValidatedOfferers).toHaveBeenCalledTimes(1)
    })

    it("should get user's venues from API", async () => {
      // When
      renderOffers({}, store)

      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledWith(null)
    })

    it('should have title "Ajouter une offre"', () => {
      // When
      renderOffers({}, store)

      // Then
      expect(screen.getByText('Nouvelle offre', { selector: 'h1' })).toBeInTheDocument()
    })

    it('should have a section "Type d\'offre"', () => {
      // When
      renderOffers({}, store)

      // Then
      expect(screen.getByText("Type d'offre", { selector: 'h2' })).toBeInTheDocument()
    })

    describe('when selecting an offer type', () => {
      it('should display "Infos pratiques", "Infos artistiques", and "Autre" section', async () => {
        // Given
        renderOffers({}, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByText('Infos artistiques', { selector: 'h2' })).toBeInTheDocument()
        expect(screen.getByText('Informations pratiques', { selector: 'h2' })).toBeInTheDocument()
        expect(screen.getByText('Autre', { selector: 'h2' })).toBeInTheDocument()
      })

      it('should display an offerer selection', async () => {
        // Given
        renderOffers({}, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.queryByLabelText('Structure')).toBeInTheDocument()
      })

      it('should have offerer selected when given as queryParam', async () => {
        // Given
        renderOffers({}, store, `?structure=${offerers[0].id}`)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
      })

      it('should have venue selected when given as queryParam', async () => {
        // Given
        renderOffers({}, store, `?lieu=${venues[0].id}`)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
      })

      it('should display a venue selection', async () => {
        // Given
        renderOffers({}, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.queryByLabelText('Lieu')).toBeInTheDocument()
      })

      it('should only display virtual venues when offer type is online only', async () => {
        // Given
        renderOffers({}, store)

        // When
        await setOfferValues({ type: 'ThingType.PRESSE_ABO' })

        // Then
        expect(screen.queryByText(venues[0].name)).not.toBeInTheDocument()
        expect(screen.queryByText(venues[1].name)).not.toBeInTheDocument()
        expect(screen.getByText(venues[2].name)).toBeInTheDocument()
      })

      it('should only display physical venues when offer type is offline only', async () => {
        // Given
        renderOffers({}, store)

        // When
        await setOfferValues({ type: 'EventType.CINEMA' })

        // Then
        expect(screen.getByText(venues[0].name)).toBeInTheDocument()
        expect(screen.getByText(venues[1].name)).toBeInTheDocument()
        expect(screen.queryByText(venues[2].name)).not.toBeInTheDocument()
      })

      it('should display all venues when offer type is offline and online', async () => {
        // Given
        renderOffers({}, store)

        // When
        await setOfferValues({ type: 'EventType.MUSIQUE' })

        // Then
        expect(screen.getByText(venues[0].name)).toBeInTheDocument()
        expect(screen.getByText(venues[1].name)).toBeInTheDocument()
        expect(screen.getByText(venues[2].name)).toBeInTheDocument()
      })

      it('should select offerer of selected venue', async () => {
        // Given
        renderOffers({}, store)
        await setOfferValues({ type: 'EventType.CINEMA' })

        // When
        await setOfferValues({ venueId: venues[0].id })

        // Then
        expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
      })

      it('should display email notification input when aksing to receive booking emails', async () => {
        // Given
        renderOffers({}, store)
        await setOfferValues({ type: 'EventType.MUSIQUE' })

        // When
        await setOfferValues({ receiveNotificationEmails: true })

        // Then
        const modifiedInputs = await setOfferValues({ bookingEmail: true })
        const { bookingEmail: bookingMailInput } = modifiedInputs

        expect(bookingMailInput).toBeInTheDocument()
        expect(bookingMailInput).toHaveAttribute('name', 'bookingEmail')
      })

      describe('with conditional field "musicType"', () => {
        it('should display a music type selection', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const musicTypeInput = screen.getByLabelText('Genre musical')
          expect(musicTypeInput).toBeInTheDocument()
          expect(musicTypeInput).toHaveAttribute('name', 'musicType')
        })

        it('should display a music subtype selection when a musicType is selected', async () => {
          // Given
          renderOffers({}, store)
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // When
          await setOfferValues({ musicType: '501' })

          // Then
          const musicSubTypeInput = screen.getByLabelText('Sous genre')
          expect(musicSubTypeInput).toBeInTheDocument()
          expect(musicSubTypeInput).toHaveAttribute('name', 'musicSubType')
        })

        it('should not display a music type selection when changing to an offer type wihtout "musicType" conditional field', async () => {
          // Given
          renderOffers({}, store)
          await setOfferValues({ type: 'EventType.MUSIQUE' })
          await screen.findByLabelText('Genre musical')

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          expect(screen.queryByLabelText('Genre musical')).not.toBeInTheDocument()
        })

        it('should not display a music subtype selection when a musicType is not selected and a showType was selected before', async () => {
          // Given
          renderOffers({}, store)
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })
          await setOfferValues({ showType: '1300' })
          await setOfferValues({ showSubType: '1307' })

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          expect(screen.queryByLabelText('Sous genre')).not.toBeInTheDocument()
        })
      })

      describe('with conditional field "showType"', () => {
        it('should display a show type selection', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })

          // Then
          const showTypeInput = screen.getByLabelText('Type de spectacle')
          expect(showTypeInput).toBeInTheDocument()
          expect(showTypeInput).toHaveAttribute('name', 'showType')
        })

        it('should display a show subtype selection when a showType is selected', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.SPECTACLE_VIVANT' })
          await setOfferValues({ showType: '1300' })

          // Then
          const showSubTypeInput = screen.getByLabelText('Sous type')
          expect(showSubTypeInput).toBeInTheDocument()
          expect(showSubTypeInput).toHaveAttribute('name', 'showSubType')
        })
      })

      describe('with conditional field "speaker"', () => {
        it('should display a text input "intervenant"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.CONFERENCE_DEBAT_DEDICACE' })

          // Then
          const speakerInput = screen.getByLabelText('Intervenant')
          expect(speakerInput).toBeInTheDocument()
          expect(speakerInput).toHaveAttribute('name', 'speaker')
        })
      })

      describe('with conditional field "author"', () => {
        it('should display a text input "auteur"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          const authorInput = screen.getByLabelText('Auteur')
          expect(authorInput).toBeInTheDocument()
          expect(authorInput).toHaveAttribute('name', 'author')
        })
      })

      describe('with conditional field "visa"', () => {
        it("should display a text input 'Visa d'exploitation'", async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          const visaInput = screen.getByLabelText(/Visa/)
          expect(visaInput).toBeInTheDocument()
          expect(visaInput).toHaveAttribute('name', 'visa')
        })
      })

      describe('with conditional field "isbn"', () => {
        it('should display a text input "ISBN"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })

          // Then
          const isbnInput = screen.getByLabelText('ISBN')
          expect(isbnInput).toBeInTheDocument()
          expect(isbnInput).toHaveAttribute('name', 'isbn')
        })
      })

      describe('with conditional field "stageDirector"', () => {
        it('should display a text input "Metteur en scène"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.CINEMA' })

          // Then
          const stageDirectorInput = screen.getByLabelText('Metteur en scène')
          expect(stageDirectorInput).toBeInTheDocument()
          expect(stageDirectorInput).toHaveAttribute('name', 'stageDirector')
        })
      })

      describe('with conditional field "performer"', () => {
        it('should display a text input "Interprète"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const performerInput = screen.getByLabelText('Interprète')
          expect(performerInput).toBeInTheDocument()
          expect(performerInput).toHaveAttribute('name', 'performer')
        })
      })

      describe('when selecting a virtual venue', () => {
        it('should display a text input "url"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })
          await setOfferValues({ venueId: venues[2].id })

          // Then
          const urlInput = screen.getByLabelText(/URL/)
          expect(urlInput).toBeInTheDocument()
          expect(urlInput).toHaveAttribute('name', 'url')
        })

        it('should display refundable banner when offer type is online only', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'ThingType.PRESSE_ABO' })
          await setOfferValues({ venueId: venues[2].id })

          // Then
          expect(
            screen.getByText(
              "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
            )
          ).toBeInTheDocument()
        })

        it('should display refundable banner when offer type is online and offline', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })
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
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'ThingType.LIVRE_EDITION' })
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
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'ThingType.CINEMA_CARD' })
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
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const durationInput = screen.getByLabelText('Durée')
          expect(durationInput).toBeInTheDocument()
          expect(durationInput).toHaveAttribute('name', 'durationMinutes')
        })

        it('should display a checkbox input "Offre duo"', async () => {
          // Given
          renderOffers({}, store)

          // When
          await setOfferValues({ type: 'EventType.MUSIQUE' })

          // Then
          const duoInput = screen.getByLabelText(/Accepter les réservations "duo"/)
          expect(duoInput).toBeInTheDocument()
          expect(duoInput).toHaveAttribute('name', 'isDuo')
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
        durationMinutes: '01:00',
        type: 'EventType.MUSIQUE',
        extraData: {
          author: '',
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        venueId: 'AB',
        isDuo: false,
        withdrawalDetails: 'À venir chercher sur place.',
      }

      renderOffers({}, store)

      await setOfferValues({ type: offerValues.type })
      await setOfferValues(offerValues)

      // When
      fireEvent.click(screen.getByText('Enregistrer et passer au stocks'))

      // Then
      expect(pcapi.createOffer).toHaveBeenCalledWith(offerValues)
    })
  })
})
