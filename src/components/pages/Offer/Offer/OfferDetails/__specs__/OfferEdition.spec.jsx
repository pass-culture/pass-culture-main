import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import NotificationV2Container from 'components/layout/NotificationV2/NotificationV2Container'
import { getProviderInfo } from 'components/pages/Offer/LocalProviderInformation/getProviderInfo'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import * as computeUrl from '../../../utils/computeOffersUrl'
import OfferLayoutContainer from '../../OfferLayoutContainer'
import { DEFAULT_FORM_VALUES } from '../OfferForm/_constants'

import { fieldLabels, findInputErrorForField, setOfferValues } from './helpers'

jest.mock('repository/pcapi/pcapi', () => ({
  updateOffer: jest.fn(),
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadOffer: jest.fn(),
  loadTypes: jest.fn(),
}))

jest.mock('../../../utils/computeOffersUrl', () => ({
  computeOffersUrl: jest.fn().mockReturnValue('/offres'),
}))

const renderOffers = async (props, store, queryParams = '') => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter
          initialEntries={[{ pathname: '/offres/v2/ABC12/edition', search: queryParams }]}
        >
          <Route path="/offres/v2/:offerId([A-Z0-9]+)/">
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

describe('offerDetails - Edition', () => {
  let editedOffer
  let offerers
  let props
  let store
  let types
  let venues

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    types = [
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
    ]
    offerers = [
      {
        id: 'BA',
        name: 'La structure',
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
    ]
    editedOffer = {
      id: 'ABC12',
      name: 'My edited offer',
      thumbUrl: null,
    }
    props = {
      setShowThumbnailForm: jest.fn(),
    }
    pcapi.loadOffer.mockResolvedValue(editedOffer)
    pcapi.loadTypes.mockResolvedValue(types)
    pcapi.getValidatedOfferers.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
  })

  describe('render when editing an existing offer', () => {
    describe('when thumbnail exists', () => {
      it('should display the actived image', async () => {
        // Given
        editedOffer.thumbUrl = 'http://example.net/active-image.png'

        // When
        renderOffers({}, store)

        // Then
        const button = await screen.findByTitle('Modifier l’image', { selector: 'button' })
        const image = await screen.findByAltText('Image de l’offre')
        expect(button).toBeInTheDocument()
        expect(image).toHaveAttribute('src', 'http://example.net/active-image.png')
      })
    })

    describe('when thumbnail do not exist', () => {
      it('should display the placeholder', async () => {
        // When
        renderOffers({}, store)

        // Then
        expect(
          await screen.findByText('Ajouter une image', { selector: 'button' })
        ).toBeInTheDocument()
      })
    })

    it('should change title with typed value', async () => {
      // Given
      await renderOffers(props, store)
      const titleInput = await screen.findByLabelText("Titre de l'offre")
      userEvent.clear(titleInput)

      // When
      userEvent.type(titleInput, 'Mon nouveau titre')

      // Then
      const newTitleValue = await screen.findByDisplayValue('Mon nouveau titre')
      expect(newTitleValue).toBeInTheDocument()
    })

    it('should show existing offer details', async () => {
      // Given
      venues[0].isVirtual = true
      const editedOffer = {
        id: 'ABC12',
        bookingEmail: 'booking@example.net',
        description: 'Offer description',
        durationMinutes: 90,
        isDuo: true,
        name: 'My edited offer',
        type: 'EventType.FULL_CONDITIONAL_FIELDS',
        url: 'http://example.net',
        venue: venues[0],
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        extraData: {
          author: 'Mr Offer Author',
          isbn: '123456789123',
          musicType: '501',
          musicSubType: '502',
          performer: 'Mr Offer Performer',
          speaker: 'Mr Offer Speaker',
          stageDirector: 'Mr Offer Stage Director',
          visa: 'Courtesy of visa',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      const fullConditionalFieldsType = {
        conditionalFields: [
          'author',
          'musicType',
          'performer',
          'isbn',
          'stageDirector',
          'speaker',
          'visa',
        ],
        offlineOnly: false,
        onlineOnly: false,
        proLabel: 'Musique - concerts, festivals',
        type: 'Event',
        value: 'EventType.FULL_CONDITIONAL_FIELDS',
      }
      pcapi.loadTypes.mockResolvedValue([fullConditionalFieldsType])

      // When
      await renderOffers(props, store)

      // Then
      const typeInput = await screen.findByLabelText(fieldLabels.type.label, {
        exact: fieldLabels.type.exact,
      })
      expect(typeInput).toHaveValue(fullConditionalFieldsType.value)
      const musicSubTypeInput = await screen.findByLabelText(fieldLabels.musicSubType.label, {
        exact: fieldLabels.musicSubType.exact,
      })
      expect(musicSubTypeInput).toHaveValue(editedOffer.musicSubType)
      const musicTypeInput = await screen.findByLabelText(fieldLabels.musicType.label, {
        exact: fieldLabels.musicType.exact,
      })
      expect(musicTypeInput).toHaveValue(editedOffer.musicType)
      const offererIdInput = await screen.findByLabelText(fieldLabels.offererId.label, {
        exact: fieldLabels.offererId.exact,
      })
      expect(offererIdInput).toHaveValue(venues[0].managingOffererId)
      const venueIdInput = await screen.findByLabelText(fieldLabels.venueId.label, {
        exact: fieldLabels.venueId.exact,
      })
      expect(venueIdInput).toHaveValue(editedOffer.venueId)

      const authorInput = await screen.findByLabelText(fieldLabels.author.label, {
        exact: fieldLabels.author.exact,
      })
      expect(authorInput).toHaveValue(editedOffer.author)
      const bookingEmailInput = await screen.findByLabelText(fieldLabels.bookingEmail.label, {
        exact: fieldLabels.bookingEmail.exact,
      })
      expect(bookingEmailInput).toHaveValue(editedOffer.bookingEmail)
      const descriptionInput = await screen.findByLabelText(fieldLabels.description.label, {
        exact: fieldLabels.description.exact,
      })
      expect(descriptionInput).toHaveValue(editedOffer.description)
      const durationMinutesInput = await screen.findByLabelText(fieldLabels.durationMinutes.label, {
        exact: fieldLabels.durationMinutes.exact,
      })
      expect(durationMinutesInput).toHaveValue('1:30')
      const isbnInput = await screen.findByLabelText(fieldLabels.isbn.label, {
        exact: fieldLabels.isbn.exact,
      })
      expect(isbnInput).toHaveValue(editedOffer.isbn)
      const isDuoInput = await screen.findByLabelText(fieldLabels.isDuo.label, {
        exact: fieldLabels.isDuo.exact,
      })
      expect(isDuoInput).toBeChecked()
      const nameInput = await screen.findByLabelText(fieldLabels.name.label, {
        exact: fieldLabels.name.exact,
      })
      expect(nameInput).toHaveValue(editedOffer.name)
      const performerInput = await screen.findByLabelText(fieldLabels.performer.label, {
        exact: fieldLabels.performer.exact,
      })
      expect(performerInput).toHaveValue(editedOffer.extraData.performer)
      const stageDirectorInput = await screen.findByLabelText(fieldLabels.stageDirector.label, {
        exact: fieldLabels.stageDirector.exact,
      })
      expect(stageDirectorInput).toHaveValue(editedOffer.extraData.stageDirector)
      const speakerInput = await screen.findByLabelText(fieldLabels.speaker.label, {
        exact: fieldLabels.speaker.exact,
      })
      expect(speakerInput).toHaveValue(editedOffer.extraData.speaker)
      const urlInput = await screen.findByLabelText(fieldLabels.url.label, {
        exact: fieldLabels.url.exact,
      })
      expect(urlInput).toHaveValue(editedOffer.url)
      const visaInput = await screen.findByLabelText(fieldLabels.visa.label, {
        exact: fieldLabels.visa.exact,
      })
      expect(visaInput).toHaveValue(editedOffer.extraData.visa)
      const withdrawalDetailsInput = await screen.findByLabelText(
        fieldLabels.withdrawalDetails.label,
        { exact: fieldLabels.withdrawalDetails.exact }
      )
      expect(withdrawalDetailsInput).toHaveValue(editedOffer.withdrawalDetails)
    })

    it('should allow edition of editable fields only', async () => {
      // Given
      venues[0].isVirtual = true
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'EventType.FULL_CONDITIONAL_FIELDS',
        description: 'Offer description',
        venue: venues[0],
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        extraData: {
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          musicType: '501',
          musicSubType: '502',
        },
        bookingEmail: 'booking@example.net',
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      types.push({
        conditionalFields: [
          'author',
          'musicType',
          'performer',
          'isbn',
          'stageDirector',
          'speaker',
          'visa',
        ],
        offlineOnly: false,
        onlineOnly: false,
        proLabel: 'Musique - concerts, festivals',
        type: 'Event',
        value: 'EventType.FULL_CONDITIONAL_FIELDS',
      })
      pcapi.loadTypes.mockResolvedValue(types)

      await renderOffers(props, store)

      // Edition read only fields
      const typeInput = await screen.findByLabelText(fieldLabels.type.label, {
        exact: fieldLabels.type.exact,
      })
      expect(typeInput).toHaveAttribute('disabled')
      const musicSubTypeInput = await screen.findByLabelText(fieldLabels.musicSubType.label, {
        exact: fieldLabels.musicSubType.exact,
      })
      expect(musicSubTypeInput).toHaveAttribute('disabled')
      const musicTypeInput = await screen.findByLabelText(fieldLabels.musicType.label, {
        exact: fieldLabels.musicType.exact,
      })
      expect(musicTypeInput).toHaveAttribute('disabled')
      const offererIdInput = await screen.findByLabelText(fieldLabels.offererId.label, {
        exact: fieldLabels.offererId.exact,
      })
      expect(offererIdInput).toHaveAttribute('disabled')
      const venueIdInput = await screen.findByLabelText(fieldLabels.venueId.label, {
        exact: fieldLabels.venueId.exact,
      })
      expect(venueIdInput).toHaveAttribute('disabled')

      // Editable fields
      const authorInput = await screen.findByLabelText(fieldLabels.author.label, {
        exact: fieldLabels.author.exact,
      })
      expect(authorInput).not.toHaveAttribute('disabled')
      const bookingEmailInput = await screen.findByLabelText(fieldLabels.bookingEmail.label, {
        exact: fieldLabels.bookingEmail.exact,
      })
      expect(bookingEmailInput).not.toHaveAttribute('disabled')
      const descriptionInput = await screen.findByLabelText(fieldLabels.description.label, {
        exact: fieldLabels.description.exact,
      })
      expect(descriptionInput).not.toHaveAttribute('disabled')
      const durationMinutesInput = await screen.findByLabelText(fieldLabels.durationMinutes.label, {
        exact: fieldLabels.durationMinutes.exact,
      })
      expect(durationMinutesInput).not.toHaveAttribute('disabled')
      const isbnInput = await screen.findByLabelText(fieldLabels.isbn.label, {
        exact: fieldLabels.isbn.exact,
      })
      expect(isbnInput).not.toHaveAttribute('disabled')
      const isDuoInput = await screen.findByLabelText(fieldLabels.isDuo.label, {
        exact: fieldLabels.isDuo.exact,
      })
      expect(isDuoInput).not.toHaveAttribute('disabled')
      const nameInput = await screen.findByLabelText(fieldLabels.name.label, {
        exact: fieldLabels.name.exact,
      })
      expect(nameInput).not.toHaveAttribute('disabled')
      const performerInput = await screen.findByLabelText(fieldLabels.performer.label, {
        exact: fieldLabels.performer.exact,
      })
      expect(performerInput).not.toHaveAttribute('disabled')
      const stageDirectorInput = await screen.findByLabelText(fieldLabels.stageDirector.label, {
        exact: fieldLabels.stageDirector.exact,
      })
      expect(stageDirectorInput).not.toHaveAttribute('disabled')
      const speakerInput = await screen.findByLabelText(fieldLabels.speaker.label, {
        exact: fieldLabels.speaker.exact,
      })
      expect(speakerInput).not.toHaveAttribute('disabled')
      const urlInput = await screen.findByLabelText(fieldLabels.url.label, {
        exact: fieldLabels.url.exact,
      })
      expect(urlInput).not.toHaveAttribute('disabled')
      const visaInput = await screen.findByLabelText(fieldLabels.visa.label, {
        exact: fieldLabels.visa.exact,
      })
      expect(visaInput).not.toHaveAttribute('disabled')
      const withdrawalDetailsInput = await screen.findByLabelText(
        fieldLabels.withdrawalDetails.label,
        { exact: fieldLabels.withdrawalDetails.exact }
      )
      expect(withdrawalDetailsInput).not.toHaveAttribute('disabled')
    })

    describe('for synchronized offers', () => {
      it('should show a banner stating the synchronization and the provider', async () => {
        // Given
        const editedOffer = {
          id: 'ABC12',
          name: 'My synchronized offer',
          type: 'ThingType.LIVRE_EDITION',
          showType: 400,
          showSubType: 401,
          description: 'Offer description',
          venue: venues[0],
          venueId: venues[0].id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'leslibraires.fr',
          },
        }
        pcapi.loadOffer.mockResolvedValue(editedOffer)
        const providerInformation = getProviderInfo(editedOffer.lastProvider.name)

        // When
        await renderOffers(props, store)

        // Then
        const providerBanner = await screen.findByText(
          `Offre synchronisée avec ${providerInformation.name}`
        )
        expect(providerBanner).toBeInTheDocument()
        expect(
          screen.getByRole('img', { name: `Icône de ${providerInformation.name}` })
        ).toHaveAttribute('src', expect.stringContaining(providerInformation.icon))
      })

      it('should not allow any edition', async () => {
        // Given
        venues[0].isVirtual = true
        const editedOffer = {
          id: 'ABC12',
          name: 'My edited offer',
          type: 'EventType.FULL_CONDITIONAL_FIELDS',
          showType: 400,
          showSubType: 401,
          description: 'Offer description',
          venue: venues[0],
          venueId: venues[0].id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'Leslibraires.fr',
          },
        }
        pcapi.loadOffer.mockResolvedValue(editedOffer)
        types.push({
          conditionalFields: [
            'author',
            'showType',
            'performer',
            'isbn',
            'stageDirector',
            'speaker',
            'visa',
          ],
          offlineOnly: false,
          onlineOnly: false,
          proLabel: 'Musique - concerts, festivals',
          type: 'Event',
          value: 'EventType.FULL_CONDITIONAL_FIELDS',
        })
        pcapi.loadTypes.mockResolvedValue(types)

        await renderOffers(props, store)

        // Edition read only fields
        const typeInput = await screen.findByLabelText(fieldLabels.type.label, {
          exact: fieldLabels.type.exact,
        })
        expect(typeInput).toHaveAttribute('disabled')
        const showSubTypeInput = await screen.findByLabelText(fieldLabels.showSubType.label, {
          exact: fieldLabels.showSubType.exact,
        })
        expect(showSubTypeInput).toHaveAttribute('disabled')
        const showTypeInput = await screen.findByLabelText(fieldLabels.showType.label, {
          exact: fieldLabels.showType.exact,
        })
        expect(showTypeInput).toHaveAttribute('disabled')
        const offererIdInput = await screen.findByLabelText(fieldLabels.offererId.label, {
          exact: fieldLabels.offererId.exact,
        })
        expect(offererIdInput).toHaveAttribute('disabled')
        const authorInput = await screen.findByLabelText(fieldLabels.author.label, {
          exact: fieldLabels.author.exact,
        })
        expect(authorInput).toHaveAttribute('disabled')
        const bookingEmailInput = await screen.findByLabelText(fieldLabels.bookingEmail.label, {
          exact: fieldLabels.bookingEmail.exact,
        })
        expect(bookingEmailInput).toHaveAttribute('disabled')
        const receiveNotificationEmailsCheckbox = await screen.findByLabelText(
          fieldLabels.receiveNotificationEmails.label,
          {
            exact: fieldLabels.bookingEmail.exact,
          }
        )
        expect(receiveNotificationEmailsCheckbox).toHaveAttribute('disabled')
        const descriptionInput = await screen.findByLabelText(fieldLabels.description.label, {
          exact: fieldLabels.description.exact,
        })
        expect(descriptionInput).toHaveAttribute('disabled')
        const durationMinutesInput = await screen.findByLabelText(
          fieldLabels.durationMinutes.label,
          {
            exact: fieldLabels.durationMinutes.exact,
          }
        )
        expect(durationMinutesInput).toHaveAttribute('disabled')
        const isbnInput = await screen.findByLabelText(fieldLabels.isbn.label, {
          exact: fieldLabels.isbn.exact,
        })
        expect(isbnInput).toHaveAttribute('disabled')
        const isDuoInput = await screen.findByLabelText(fieldLabels.isDuo.label, {
          exact: fieldLabels.isDuo.exact,
        })
        expect(isDuoInput).toHaveAttribute('disabled')
        const nameInput = await screen.findByLabelText(fieldLabels.name.label, {
          exact: fieldLabels.name.exact,
        })
        expect(nameInput).toHaveAttribute('disabled')
        const performerInput = await screen.findByLabelText(fieldLabels.performer.label, {
          exact: fieldLabels.performer.exact,
        })
        expect(performerInput).toHaveAttribute('disabled')
        const stageDirectorInput = await screen.findByLabelText(fieldLabels.stageDirector.label, {
          exact: fieldLabels.stageDirector.exact,
        })
        expect(stageDirectorInput).toHaveAttribute('disabled')
        const speakerInput = await screen.findByLabelText(fieldLabels.speaker.label, {
          exact: fieldLabels.speaker.exact,
        })
        expect(speakerInput).toHaveAttribute('disabled')
        const urlInput = await screen.findByLabelText(fieldLabels.url.label, {
          exact: fieldLabels.url.exact,
        })
        expect(urlInput).toHaveAttribute('disabled')
        const venueIdInput = await screen.findByLabelText(fieldLabels.venueId.label, {
          exact: fieldLabels.venueId.exact,
        })
        expect(venueIdInput).toHaveAttribute('disabled')
        const visaInput = await screen.findByLabelText(fieldLabels.visa.label, {
          exact: fieldLabels.visa.exact,
        })
        expect(visaInput).toHaveAttribute('disabled')
        const withdrawalDetailsInput = await screen.findByLabelText(
          fieldLabels.withdrawalDetails.label,
          { exact: fieldLabels.withdrawalDetails.exact }
        )
        expect(withdrawalDetailsInput).toHaveAttribute('disabled')
      })

      it('should allow edition of "isDuo" for "Allociné" offers', async () => {
        const editedOffer = {
          id: 'ABC12',
          name: 'My edited offer',
          type: 'EventType.CINEMA',
          showType: 400,
          showSubType: 401,
          description: 'Offer description',
          venue: venues[0],
          venueId: venues[0].id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'Allociné',
          },
        }
        pcapi.loadOffer.mockResolvedValue(editedOffer)
        const cinemaType = {
          conditionalFields: ['author', 'visa', 'stageDirector'],
          offlineOnly: true,
          onlineOnly: false,
          proLabel: 'Cinéma - projections et autres évènements',
          type: 'Event',
          value: 'EventType.CINEMA',
        }
        pcapi.loadTypes.mockResolvedValue([cinemaType])

        await renderOffers(props, store)

        // Edition read only fields
        const isDuoInput = await screen.findByLabelText(fieldLabels.isDuo.label, {
          exact: fieldLabels.isDuo.exact,
        })
        expect(isDuoInput).not.toHaveAttribute('disabled')
      })
    })
  })

  describe('when submitting form', () => {
    it('should not send not editable fields for unsynchronised offers', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.LIVRE_EDITION',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: null,
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      expect(pcapi.updateOffer).toHaveBeenCalledWith(
        editedOffer.id,
        expect.not.objectContaining({
          venueId: expect.anything(),
          type: expect.anything(),
        })
      )
    })

    it('should show a success notification when form was correctly submitted', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.LIVRE_EDITION',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: null,
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const successNotification = await screen.findByText('Votre offre a bien été modifiée')
      expect(successNotification).toBeInTheDocument()
    })

    it('should not send extraData for synchronized offers', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'EventType.CINEMA',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          stageDirector: 'Mr Stage Director',
        },
        lastProvider: {
          name: 'Allociné',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      const cinemaType = {
        conditionalFields: ['author', 'visa', 'stageDirector'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Cinéma - projections et autres évènements',
        type: 'Event',
        value: 'EventType.CINEMA',
      }
      pcapi.loadTypes.mockResolvedValue([cinemaType])

      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      expect(pcapi.updateOffer).toHaveBeenCalledWith(
        editedOffer.id,
        expect.not.objectContaining({
          extraData: null,
        })
      )
    })

    it('should send null extraData when removing them', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.LIVRE_EDITION',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          author: 'Mon auteur',
          isbn: '123456789',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      await setOfferValues({ author: DEFAULT_FORM_VALUES.author, isbn: DEFAULT_FORM_VALUES.isbn })

      // Then
      userEvent.click(screen.getByText('Enregistrer'))
      expect(pcapi.updateOffer).toHaveBeenCalledWith(
        editedOffer.id,
        expect.objectContaining({
          extraData: null,
        })
      )
    })

    it('should remove attribute from extraData when no value is provided', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.LIVRE_EDITION',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          author: 'Mon auteur',
          isbn: '123456789',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      await setOfferValues({ author: DEFAULT_FORM_VALUES.author })

      // Then
      userEvent.click(screen.getByText('Enregistrer'))
      expect(pcapi.updateOffer).toHaveBeenCalledWith(
        editedOffer.id,
        expect.objectContaining({
          extraData: { isbn: editedOffer.extraData.isbn },
        })
      )
    })

    it('should remove notification email when remove the will to receive notifications', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.LIVRE_EDITION',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: null,
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)
      await setOfferValues({ receiveNotificationEmails: false })

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      expect(pcapi.updateOffer).toHaveBeenCalledWith(
        editedOffer.id,
        expect.objectContaining({
          bookingEmail: null,
        })
      )
    })

    it('should show error for email notification input when asking to receive booking emails and no email was provided', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.PRESSE_ABO',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: null,
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)
      await setOfferValues({ receiveNotificationEmails: true })

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const bookingEmailInput = await findInputErrorForField('bookingEmail')
      expect(bookingEmailInput).toHaveTextContent('Ce champ est obligatoire')
      expect(
        screen.getByText('Une ou plusieurs erreurs sont présentes dans le formulaire')
      ).toBeInTheDocument()
    })
  })

  describe('when clicking on cancel link', () => {
    it('should call computeOffersUrl with proper params', async () => {
      // Given
      store = configureTestStore({
        data: { users: [{ publicName: 'François', isAdmin: false }] },
        offers: {
          searchFilters: {
            name: 'test',
            offererId: 'AY',
            venueId: 'EQ',
            typeId: 'EventType.CINEMA',
            status: 'all',
            creationMode: 'manual',
            periodBeginningDate: '2020-11-30T00:00:00+01:00',
            periodEndingDate: '2021-01-07T23:59:59+01:00',
            page: 1,
          },
        },
      })
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.LIVRE_EDITION',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: null,
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Annuler'))

      // Then
      expect(computeUrl.computeOffersUrl).toHaveBeenLastCalledWith({
        creationMode: 'manual',
        name: 'test',
        offererId: 'AY',
        page: 1,
        periodBeginningDate: '2020-11-30T00:00:00+01:00',
        periodEndingDate: '2021-01-07T23:59:59+01:00',
        status: 'all',
        typeId: 'EventType.CINEMA',
        venueId: 'EQ',
      })
    })

    it('should redirect to offers page', async () => {
      // Given
      store = configureTestStore({
        data: { users: [{ publicName: 'François', isAdmin: false }] },
        offers: {
          searchFilters: {},
        },
      })
      const editedOffer = {
        id: 'ABC12',
        name: 'My edited offer',
        type: 'ThingType.PRESSE_ABO',
        description: 'Offer description',
        venueId: venues[0].id,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: null,
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)

      // When
      await renderOffers(props, store)

      // Then
      const cancelLink = await screen.findByText('Annuler', { selector: 'a' })
      expect(cancelLink).toBeInTheDocument()
      expect(cancelLink).toHaveAttribute('href', '/offres')
    })
  })
})
