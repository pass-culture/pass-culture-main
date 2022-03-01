import '@testing-library/jest-dom'
import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { apiV1 } from 'api/api'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import { getProviderInfo } from 'components/pages/Offers/domain/getProviderInfo'
import OfferLayoutContainer from 'components/pages/Offers/Offer/OfferLayoutContainer'
import * as computeUrl from 'components/pages/Offers/utils/computeOffersUrl'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import { DEFAULT_FORM_VALUES } from '../_constants'

import {
  fieldLabels,
  findInputErrorForField,
  getOfferInputForField,
  setOfferValues,
} from './helpers'

Element.prototype.scrollIntoView = () => {}

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
  getVenue: jest.fn(),
  loadCategories: jest.fn(),
  loadStocks: jest.fn(),
  postThumbnail: jest.fn(),
  updateOffer: jest.fn(),
}))

jest.mock('../../../utils/computeOffersUrl', () => ({
  computeOffersUrl: jest.fn().mockReturnValue('/offres'),
}))

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn().mockReturnValue(false),
}))

const renderOffers = async (props, store, queryParams = '') => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter
          initialEntries={[
            {
              pathname: '/offre/ABC12/individuel/edition',
              search: queryParams,
            },
          ]}
        >
          <Route path="/offre/:offerId([A-Z0-9]+)/individuel">
            <>
              <OfferLayoutContainer {...props} />
              <NotificationContainer />
            </>
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offerDetails - Edition', () => {
  let editedOffer
  let venueManagingOfferer
  let props
  let store
  let editedOfferVenue
  let categories

  beforeEach(() => {
    store = configureTestStore({
      data: {
        users: [
          {
            publicName: 'François',
            isAdmin: false,
            email: 'francois@example.com',
          },
        ],
      },
    })

    venueManagingOfferer = {
      id: 'BA',
      name: 'La structure',
    }

    editedOfferVenue = {
      id: 'AB',
      isVirtual: false,
      managingOfferer: venueManagingOfferer,
      managingOffererId: venueManagingOfferer.id,
      name: 'Le lieu',
      offererName: 'La structure',
      bookingEmail: 'venue@example.com',
      withdrawalDetails: null,
      audioDisabilityCompliant: null,
      mentalDisabilityCompliant: null,
      motorDisabilityCompliant: null,
      visualDisabilityCompliant: null,
    }

    editedOffer = {
      id: 'ABC12',
      nonHumanizedId: 111,
      subcategoryId: 'ID',
      name: 'My edited offer',
      venue: editedOfferVenue,
      venueId: editedOfferVenue.id,
      thumbUrl: null,
      description: 'My edited description',
      withdrawalDetails: 'My edited withdrawal details',
      status: 'SOLD_OUT',
      extraData: {
        isbn: '1234567890123',
      },
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: false,
    }

    categories = {
      categories: [
        {
          id: 'ID',
          name: 'Musique',
          proLabel: 'Musique',
          appLabel: 'Musique',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: 'ID',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: true,
          canBeEducational: true,
          isSelectable: true,
        },
        {
          id: 'ID2',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: false,
          canBeEducational: true,
          isSelectable: true,
        },
      ],
    }

    props = {
      setShowThumbnailForm: jest.fn(),
    }
    jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
    pcapi.loadCategories.mockResolvedValue(categories)
    pcapi.getVenue.mockReturnValue(Promise.resolve())
    pcapi.loadStocks.mockReturnValue(Promise.resolve({ stocks: [] }))
  })

  describe('render when editing an existing offer', () => {
    describe('when interacting with disability fields', () => {
      describe('for offers without any disability compliance information', () => {
        beforeEach(async () => {
          const editedOffer = {
            id: 'ABC12',
            nonHumanizedId: 111,
            subcategoryId: 'ID',
            name: 'My edited offer',
            venue: editedOfferVenue,
            thumbUrl: null,
            audioDisabilityCompliant: null,
            mentalDisabilityCompliant: null,
            motorDisabilityCompliant: null,
            visualDisabilityCompliant: null,
            status: 'ACTIVE',
          }
          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

          // When
          await renderOffers(props, store)
        })

        it('should display error when submitting empty values', async () => {
          // When
          userEvent.click(screen.getByText('Enregistrer'))

          // Then
          const errorNotification = await screen.findByText(
            'Une ou plusieurs erreurs sont présentes dans le formulaire'
          )
          expect(errorNotification).toBeInTheDocument()
          let accessibilityErrorNotification = await screen.findByText(
            'Veuillez cocher au moins une option ci-dessus'
          )
          expect(accessibilityErrorNotification).toBeInTheDocument()
          expect(pcapi.updateOffer).not.toHaveBeenCalled()

          // When
          const mentalDisabilityCompliantCheckbox = screen.getByLabelText(
            fieldLabels.mentalDisabilityCompliant.label,
            {
              exact: fieldLabels.mentalDisabilityCompliant.exact,
            }
          )
          userEvent.click(mentalDisabilityCompliantCheckbox)

          // Then
          accessibilityErrorNotification = screen.queryByText(
            'Vous devez cocher l’une des options ci-dessus'
          )
          expect(accessibilityErrorNotification).toBeNull()
        })
      })
    })

    describe('when thumbnail exists', () => {
      it('should display the actived image', async () => {
        // Given
        editedOffer.thumbUrl = 'http://example.net/active-image.png'

        // When
        await renderOffers({}, store)

        // Then
        const button = await screen.findByTitle('Modifier l’image', {
          selector: 'button',
        })
        const image = await screen.findByAltText('Image de l’offre')
        expect(button).toBeInTheDocument()
        expect(image).toHaveAttribute(
          'src',
          'http://example.net/active-image.png'
        )
      })

      it('should close the modal when user is clicking on close button', async () => {
        // Given
        editedOffer.thumbUrl = 'http://example.net/active-image.png'
        await renderOffers({}, store)
        userEvent.click(
          await screen.findByTitle('Modifier l’image', { selector: 'button' })
        )

        // When
        userEvent.click(
          await screen.findByTitle('Fermer la modale', { selector: 'button' })
        )

        // Then
        expect(
          screen.getByTitle('Modifier l’image', { selector: 'button' })
        ).toBeInTheDocument()
        expect(
          screen.queryByTitle('Fermer la modale', { selector: 'button' })
        ).not.toBeInTheDocument()
      })

      it("should have a preview link redirecting to the webapp's offer page", async () => {
        // When
        editedOffer.thumbUrl = 'http://example.net/active-image.png'
        await renderOffers({}, store)

        // Then
        const previewLink = await screen.findByText('Visualiser dans l’app', {
          selector: 'a',
        })
        expect(previewLink).toBeInTheDocument()
        const expectedWebappUri = `offre/${editedOffer.nonHumanizedId}`
        expect(previewLink).toHaveAttribute(
          'href',
          expect.stringContaining(expectedWebappUri)
        )
      })

      it("should have a preview link redirecting to the webapp's offer page with mediationId as parameter when an active mediation exists", async () => {
        // Given
        editedOffer.thumbUrl = 'http://example.net/active-image.png'

        // When
        await renderOffers({}, store)

        // Then
        const previewLink = await screen.findByText('Visualiser dans l’app', {
          selector: 'a',
        })
        expect(previewLink).toBeInTheDocument()
        const expectedWebappUri = `offre/`
        expect(previewLink).toHaveAttribute(
          'href',
          expect.stringContaining(expectedWebappUri)
        )
      })
    })

    describe('when thumbnail does not exist', () => {
      it('should display the placeholder', async () => {
        // When
        await renderOffers({}, store)

        // Then
        expect(
          screen.getByText('Ajouter une image', { selector: 'button' })
        ).toBeInTheDocument()
      })

      it('should open the modal when user clicks on the placeholder', async () => {
        // Given
        await renderOffers({}, store)

        // When
        userEvent.click(
          await screen.findByTitle('Ajouter une image', { selector: 'button' })
        )

        // Then
        await expect(
          screen.findByLabelText('Ajouter une image')
        ).resolves.toBeInTheDocument()
      })
    })

    describe('offer preview', () => {
      it('should display title', async () => {
        // when
        await renderOffers({}, store)

        // then
        const offerPreview = screen.getByTestId('offer-preview-section')
        expect(
          within(offerPreview).getByText(editedOffer.name)
        ).toBeInTheDocument()
      })

      it('should display description', async () => {
        // when
        await renderOffers({}, store)

        // then
        const offerPreview = screen.getByTestId('offer-preview-section')
        expect(
          within(offerPreview).getByText(editedOffer.description)
        ).toBeInTheDocument()
      })

      it('should display terms of withdrawal', async () => {
        // when
        await renderOffers({}, store)

        // then
        const offerPreview = screen.getByTestId('offer-preview-section')
        expect(
          within(offerPreview).getByText(editedOffer.withdrawalDetails)
        ).toBeInTheDocument()
      })

      describe('when fraud detection', () => {
        let fullConditionalFieldsCategoryResponse = {}
        const fieldNames = { ...fieldLabels }
        delete fieldNames.isNational
        delete fieldNames.showSubType
        delete fieldNames.showType
        delete fieldNames.url

        beforeEach(() => {
          editedOffer = {
            ...editedOffer,
            bookingEmail: 'booking@example.net',
            isDuo: true,
            audioDisabilityCompliant: true,
            mentalDisabilityCompliant: true,
            motorDisabilityCompliant: true,
            visualDisabilityCompliant: true,
            url: 'http://example.net',
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

          fullConditionalFieldsCategoryResponse = {
            ...categories,
            subcategories: [
              {
                ...categories.subcategories[0],
                isEvent: true,
                conditionalFields: [
                  'author',
                  'isbn',
                  'musicType',
                  'performer',
                  'speaker',
                  'stageDirector',
                  'visa',
                ],
              },
            ],
          }
        })

        it('should display status informative message and disable all fields when offer is rejected', async () => {
          // given
          editedOffer.status = 'REJECTED'
          editedOffer.isActive = false
          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
          pcapi.loadCategories.mockResolvedValue(
            fullConditionalFieldsCategoryResponse
          )

          // when
          await renderOffers({}, store)

          // then
          expect(
            screen.getByText(
              'Votre offre a été refusée car elle ne respecte pas les Conditions Générales d’Utilisation du pass. Un e-mail contenant les conditions d’éligibilité d’une offre a été envoyé à l’adresse e-mail attachée à votre compte.'
            )
          ).toBeInTheDocument()

          for (const fieldName in fieldNames) {
            expect(
              screen.getByLabelText(fieldNames[fieldName].label, {
                exact: fieldNames[fieldName].exact,
              })
            ).toBeDisabled()
          }
          expect(screen.getByLabelText('Aucune')).toBeDisabled()
          expect(screen.getByText('Enregistrer')).toBeDisabled()
          expect(screen.getByTitle('Ajouter une image')).toBeDisabled()
        })

        it('should display status informative message and disable all fields when offer is pending for validation', async () => {
          // given
          editedOffer.status = 'PENDING'
          editedOffer.isActive = true
          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
          pcapi.loadCategories.mockResolvedValue(
            fullConditionalFieldsCategoryResponse
          )

          // when
          await renderOffers({}, store)

          // then
          expect(
            screen.getByText(
              'Votre offre est en cours de validation par l’équipe du pass Culture. Une fois validée, vous recevrez un e-mail de confirmation et votre offre sera automatiquement mise en ligne.'
            )
          ).toBeInTheDocument()
          for (const fieldName in fieldNames) {
            expect(
              screen.getByLabelText(fieldNames[fieldName].label, {
                exact: fieldNames[fieldName].exact,
              })
            ).toBeDisabled()
          }
          expect(screen.getByLabelText('Aucune')).toBeDisabled()
          expect(screen.getByText('Enregistrer')).toBeDisabled()
          expect(screen.getByTitle('Ajouter une image')).toBeDisabled()
        })
      })
    })

    it('should change title with typed value', async () => {
      // Given
      await renderOffers(props, store)
      const titleInput = await screen.findByLabelText("Titre de l'offre", {
        exact: false,
      })
      userEvent.clear(titleInput)

      // When
      userEvent.type(titleInput, 'Mon nouveau titre')

      // Then
      const newTitleValue = await screen.findByDisplayValue('Mon nouveau titre')
      expect(newTitleValue).toBeInTheDocument()
    })

    it('should show existing offer details', async () => {
      // Given
      editedOfferVenue.isVirtual = true
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        bookingEmail: 'booking@example.net',
        description: 'Offer description',
        durationMinutes: 90,
        externalTicketOfficeUrl: 'http://example.fr',
        isDuo: true,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        name: 'My edited offer',
        url: 'http://example.net',
        venue: editedOfferVenue,
        venueId: editedOfferVenue.id,
        withdrawalDetails: 'Offer withdrawal details',
        status: 'ACTIVE',
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
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      const fullConditionalFieldsCategoryResponse = {
        ...categories,
        subcategories: [
          {
            ...categories.subcategories[0],
            isEvent: true,
            conditionalFields: [
              'author',
              'isbn',
              'musicType',
              'performer',
              'speaker',
              'stageDirector',
              'visa',
            ],
          },
        ],
      }

      pcapi.loadCategories.mockResolvedValue(
        fullConditionalFieldsCategoryResponse
      )

      // When
      await renderOffers(props, store)

      // Then
      const categoryInput = screen.getByLabelText(
        fieldLabels.categoryId.label,
        {
          exact: fieldLabels.categoryId.exact,
        }
      )
      expect(categoryInput).toHaveValue(
        categories.subcategories[0].categoryId.toString()
      )

      const musicSubTypeInput = screen.getByLabelText(
        fieldLabels.musicSubType.label,
        {
          exact: fieldLabels.musicSubType.exact,
        }
      )
      expect(musicSubTypeInput).toHaveValue(editedOffer.musicSubType)
      const musicTypeInput = screen.getByLabelText(
        fieldLabels.musicType.label,
        {
          exact: fieldLabels.musicType.exact,
        }
      )
      expect(musicTypeInput).toHaveValue(editedOffer.musicType)
      const offererIdInput = screen.getByLabelText(
        fieldLabels.offererId.label,
        {
          exact: fieldLabels.offererId.exact,
        }
      )
      expect(offererIdInput).toHaveValue(editedOfferVenue.managingOffererId)
      const venueIdInput = screen.getByLabelText(fieldLabels.venueId.label, {
        exact: fieldLabels.venueId.exact,
      })
      expect(venueIdInput).toHaveValue(editedOffer.venueId)

      const authorInput = screen.getByLabelText(fieldLabels.author.label, {
        exact: fieldLabels.author.exact,
      })
      expect(authorInput).toHaveValue(editedOffer.author)
      const bookingEmailInput = screen.getByLabelText(
        fieldLabels.bookingEmail.label,
        {
          exact: fieldLabels.bookingEmail.exact,
        }
      )
      expect(bookingEmailInput).toHaveValue(editedOffer.bookingEmail)
      const descriptionInput = screen.getByLabelText(
        fieldLabels.description.label,
        {
          exact: fieldLabels.description.exact,
        }
      )
      expect(descriptionInput).toHaveValue(editedOffer.description)
      const durationMinutesInput = screen.getByLabelText(
        fieldLabels.durationMinutes.label,
        {
          exact: fieldLabels.durationMinutes.exact,
        }
      )
      expect(durationMinutesInput).toHaveValue('1:30')
      const isbnInput = screen.getByLabelText(fieldLabels.isbn.label, {
        exact: fieldLabels.isbn.exact,
      })
      expect(isbnInput).toHaveValue(editedOffer.isbn)
      const isDuoInput = screen.getByLabelText(fieldLabels.isDuo.label, {
        exact: fieldLabels.isDuo.exact,
      })
      expect(isDuoInput).toBeChecked()
      const audioDisabilityCompliantInput = screen.getByLabelText(
        fieldLabels.audioDisabilityCompliant.label,
        {
          exact: fieldLabels.audioDisabilityCompliant.exact,
        }
      )
      expect(audioDisabilityCompliantInput).toBeChecked()
      const mentalDisabilityCompliantInput = screen.getByLabelText(
        fieldLabels.mentalDisabilityCompliant.label,
        {
          exact: fieldLabels.mentalDisabilityCompliant.exact,
        }
      )
      expect(mentalDisabilityCompliantInput).toBeChecked()
      const motorDisabilityCompliantInput = screen.getByLabelText(
        fieldLabels.motorDisabilityCompliant.label,
        {
          exact: fieldLabels.motorDisabilityCompliant.exact,
        }
      )
      expect(motorDisabilityCompliantInput).toBeChecked()
      const visualDisabilityCompliantInput = screen.getByLabelText(
        fieldLabels.visualDisabilityCompliant.label,
        {
          exact: fieldLabels.visualDisabilityCompliant.exact,
        }
      )
      expect(visualDisabilityCompliantInput).toBeChecked()
      const nameInput = screen.getByLabelText(fieldLabels.name.label, {
        exact: fieldLabels.name.exact,
      })
      expect(nameInput).toHaveValue(editedOffer.name)
      const performerInput = screen.getByLabelText(
        fieldLabels.performer.label,
        {
          exact: fieldLabels.performer.exact,
        }
      )
      expect(performerInput).toHaveValue(editedOffer.extraData.performer)
      const stageDirectorInput = screen.getByLabelText(
        fieldLabels.stageDirector.label,
        {
          exact: fieldLabels.stageDirector.exact,
        }
      )
      expect(stageDirectorInput).toHaveValue(
        editedOffer.extraData.stageDirector
      )
      const speakerInput = screen.getByLabelText(fieldLabels.speaker.label, {
        exact: fieldLabels.speaker.exact,
      })
      expect(speakerInput).toHaveValue(editedOffer.extraData.speaker)
      const externalTicketOfficeUrlInput = screen.getByLabelText(
        fieldLabels.externalTicketOfficeUrl.label,
        {
          exact: fieldLabels.externalTicketOfficeUrl.exact,
        }
      )
      expect(externalTicketOfficeUrlInput).toHaveValue(
        editedOffer.externalTicketOfficeUrl
      )
      const urlInput = screen.getByLabelText(fieldLabels.url.label, {
        exact: fieldLabels.url.exact,
      })
      expect(urlInput).toHaveValue(editedOffer.url)
      const visaInput = screen.getByLabelText(fieldLabels.visa.label, {
        exact: fieldLabels.visa.exact,
      })
      expect(visaInput).toHaveValue(editedOffer.extraData.visa)
      const withdrawalDetailsInput = screen.getByLabelText(
        fieldLabels.withdrawalDetails.label,
        {
          exact: fieldLabels.withdrawalDetails.exact,
        }
      )
      expect(withdrawalDetailsInput).toHaveValue(editedOffer.withdrawalDetails)
    })

    it('should allow edition of editable fields only', async () => {
      // Given
      editedOfferVenue.isVirtual = true
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venue: editedOfferVenue,
        venueId: editedOfferVenue.id,
        withdrawalDetails: 'Offer withdrawal details',
        extraData: {
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          musicType: '501',
          musicSubType: '502',
        },
        bookingEmail: 'booking@example.net',
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      const fullConditionalFieldsCategoryResponse = {
        ...categories,
        subcategories: [
          {
            ...categories.subcategories[0],
            isEvent: true,
            conditionalFields: [
              'author',
              'isbn',
              'musicType',
              'showType',
              'performer',
              'speaker',
              'stageDirector',
              'visa',
            ],
          },
        ],
      }

      pcapi.loadCategories.mockResolvedValue(
        fullConditionalFieldsCategoryResponse
      )

      // When
      await renderOffers(props, store)

      // Then
      // Edition read only fields
      const disabledFields = [
        'categoryId',
        'musicSubType',
        'musicType',
        'offererId',
        'venueId',
      ]

      disabledFields.forEach(label => {
        const input = screen.getByLabelText(fieldLabels[label].label, {
          exact: fieldLabels[label].exact,
        })
        expect(input).toBeDisabled()
      })

      // Editable fields
      const editableFields = [
        'author',
        'bookingEmail',
        'description',
        'durationMinutes',
        'isbn',
        'isDuo',
        'name',
        'performer',
        'stageDirector',
        'speaker',
        'externalTicketOfficeUrl',
        'url',
        'visa',
        'withdrawalDetails',
        'audioDisabilityCompliant',
        'motorDisabilityCompliant',
        'visualDisabilityCompliant',
      ]

      editableFields.forEach(label => {
        const input = screen.getByLabelText(fieldLabels[label].label, {
          exact: fieldLabels[label].exact,
        })
        expect(input).toBeEnabled()
      })
      expect(screen.getByLabelText('Aucune')).toBeEnabled()
    })

    it("should display venue's publicName instead of name if exists", async () => {
      // Given
      editedOfferVenue.publicName = 'Le publicName du lieu'
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      // When
      await renderOffers(props, store)

      // Then
      expect(screen.queryByText(editedOfferVenue.name)).not.toBeInTheDocument()
      expect(screen.getByText(editedOfferVenue.publicName)).toBeInTheDocument()
    })

    describe('for synchronized offers', () => {
      it('should show a banner stating the synchronization and the provider', async () => {
        // Given
        const editedOffer = {
          id: 'ABC12',
          nonHumanizedId: 111,
          subcategoryId: 'ID',
          name: 'My synchronized offer',
          showType: 400,
          showSubType: 401,
          description: 'Offer description',
          venue: editedOfferVenue,
          venueId: editedOfferVenue.id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'leslibraires.fr',
          },
          status: 'ACTIVE',
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
        const providerInformation = getProviderInfo(
          editedOffer.lastProvider.name
        )

        // When
        await renderOffers(props, store)

        // Then
        const providerBanner = await screen.findByText(
          `Offre synchronisée avec ${providerInformation.name}`
        )
        expect(providerBanner).toBeInTheDocument()
        expect(
          screen.getByRole('img', {
            name: `Icône de ${providerInformation.name}`,
          })
        ).toHaveAttribute(
          'src',
          expect.stringContaining(providerInformation.icon)
        )
      })

      it('should allow edition of accessibility fields and external ticket office url', async () => {
        // Given
        editedOfferVenue.isVirtual = true
        const editedOffer = {
          id: 'ABC12',
          nonHumanizedId: 111,
          subcategoryId: 'ID',
          name: 'My edited offer',
          showType: 400,
          showSubType: 401,
          description: 'Offer description',
          venue: editedOfferVenue,
          venueId: editedOfferVenue.id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'Leslibraires.fr',
          },
          status: 'ACTIVE',
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

        // when
        await renderOffers(props, store)

        const editableFields = [
          'mentalDisabilityCompliant',
          'externalTicketOfficeUrl',
          'audioDisabilityCompliant',
          'motorDisabilityCompliant',
          'visualDisabilityCompliant',
        ]

        // then
        editableFields.forEach(label => {
          const input = screen.getByLabelText(fieldLabels[label].label, {
            exact: fieldLabels[label].exact,
          })
          expect(input).toBeEnabled()
        })
      })

      it('should not allow any other edition', async () => {
        // Given
        editedOfferVenue.isVirtual = true
        const editedOffer = {
          id: 'ABC12',
          nonHumanizedId: 111,
          subcategoryId: 'ID',
          name: 'My edited offer',
          showType: '400',
          showSubType: '401',
          description: 'Offer description',
          venue: editedOfferVenue,
          venueId: editedOfferVenue.id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'Leslibraires.fr',
          },
          status: 'ACTIVE',
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

        const fullConditionalFieldsCategoryResponse = {
          ...categories,
          subcategories: [
            {
              ...categories.subcategories[0],
              isEvent: true,
              conditionalFields: [
                'author',
                'showType',
                'performer',
                'isbn',
                'stageDirector',
                'speaker',
                'visa',
              ],
            },
          ],
        }

        pcapi.loadCategories.mockResolvedValue(
          fullConditionalFieldsCategoryResponse
        )

        // When
        await renderOffers(props, store)

        // Then
        // Edition read only fields
        const disabledFields = [
          'categoryId',
          'subcategoryId',
          'showType',
          'showSubType',
          'offererId',
          'author',
          'bookingEmail',
          'receiveNotificationEmails',
          'description',
          'durationMinutes',
          'isbn',
          'isDuo',
          'name',
          'performer',
          'stageDirector',
          'speaker',
          'url',
          'venueId',
          'visa',
          'withdrawalDetails',
        ]

        disabledFields.forEach(label => {
          const input = screen.getByLabelText(fieldLabels[label].label, {
            exact: fieldLabels[label].exact,
          })
          expect(input).toBeDisabled()
        })
        expect(screen.getByLabelText('Aucune')).toBeDisabled()
      })

      it('should not allow to edit duo option when offer cannot be educational', async () => {
        // Given
        const editedOffer = {
          id: 'ABC12',
          nonHumanizedId: 111,
          subcategoryId: 'ID',
          name: 'My edited offer',
          description: 'Offer description',
          venue: editedOfferVenue,
          venueId: editedOfferVenue.id,
          withdrawalDetails: 'Offer withdrawal details',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'Leslibraires.fr',
          },
          status: 'ACTIVE',
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

        const nonEducationalCategoryResponse = {
          ...categories,
          subcategories: [
            {
              ...categories.subcategories[0],
              isEvent: true,
              canBeEducational: false,
            },
          ],
        }

        pcapi.loadCategories.mockResolvedValue(nonEducationalCategoryResponse)

        // When
        await renderOffers(props, store)

        // Then
        const duoOption = await getOfferInputForField('isDuo')
        expect(duoOption).toBeDisabled()
        expect(screen.getByLabelText('Aucune')).toBeDisabled()
      })

      it('should allow edition of "isDuo" for "Allociné" offers', async () => {
        // Given
        const editedOffer = {
          id: 'ABC12',
          nonHumanizedId: 111,
          subcategoryId: 'ID',
          name: 'My edited offer',
          showType: 400,
          showSubType: 401,
          description: 'Offer description',
          venue: editedOfferVenue,
          venueId: editedOfferVenue.id,
          withdrawalDetails: 'Offer withdrawal details',
          author: 'Mr Offer Author',
          performer: 'Mr Offer Performer',
          bookingEmail: 'booking@example.net',
          lastProvider: {
            name: 'Allociné',
          },
          status: 'ACTIVE',
        }

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

        const fullConditionalFieldsCategoryResponse = {
          ...categories,
          subcategories: [
            {
              ...categories.subcategories[0],
              isEvent: true,
            },
          ],
        }

        pcapi.loadCategories.mockResolvedValue(
          fullConditionalFieldsCategoryResponse
        )

        // When
        await renderOffers(props, store)

        // Then
        const isDuoInput = await getOfferInputForField('isDuo')
        expect(isDuoInput).toBeEnabled()
        expect(screen.getByLabelText('Aucune')).toBeEnabled()
      })
    })

    describe('when booking email checkbox is not checked yet and user checks it', () => {
      it('should prefill booking email input with correct value', async () => {
        // given
        const editedOffer = {
          id: 'ABC12',
          nonHumanizedId: 111,
          subcategoryId: 'ID',
          name: 'My edited offer',
          description: 'Offer description',
          venueId: editedOfferVenue.id,
          venue: editedOfferVenue,
          withdrawalDetails: 'Offer withdrawal details',
          bookingEmail: null,
          extraData: null,
          audioDisabilityCompliant: false,
          mentalDisabilityCompliant: false,
          motorDisabilityCompliant: false,
          visualDisabilityCompliant: false,
          status: 'ACTIVE',
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
        await renderOffers(props, store)

        // when
        await act(async () => {
          await setOfferValues({ receiveNotificationEmails: true })
        })

        // then
        expect(
          screen.getByLabelText('Email auquel envoyer les notifications :')
            .value
        ).toBe('venue@example.com')
      })
    })
  })

  describe('when submitting form', () => {
    it('should show updated fields when going and back to stock tab', async () => {
      // Given
      await renderOffers(props, store)
      const editValues = {
        name: 'My edited offer',
        subcategoryId: 'ID',
        description: 'Offer description edited',
        withdrawalDetails: 'Offer withdrawal details edited',
        audioDisabilityCompliant: true,
        visualDisabilityCompliant: false,
        motorDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
      }

      // When
      await setOfferValues({ subcategoryId: editValues.subcategoryId })
      await setOfferValues(editValues)
      const newEditedOffer = { ...editedOffer, ...editValues }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(newEditedOffer)
      fireEvent.click(screen.getByText('Enregistrer'))
      fireEvent.click(screen.getByText('Stock et prix'))
      fireEvent.click(await screen.findByText("Détails de l'offre"))

      // Then
      await expect(getOfferInputForField('name')).resolves.toHaveValue(
        editValues.name
      )

      const expectedSubCategoryValue = categories.subcategories.find(
        subCat => subCat.id.toString() === editValues.subcategoryId
      ).proLabel
      await expect(
        getOfferInputForField('subcategoryId')
      ).resolves.toHaveTextContent(expectedSubCategoryValue)

      await expect(
        getOfferInputForField('description')
      ).resolves.toHaveTextContent(editValues.description)
      await expect(
        getOfferInputForField('withdrawalDetails')
      ).resolves.toHaveTextContent(editValues.withdrawalDetails)
      await expect(
        getOfferInputForField('audioDisabilityCompliant')
      ).resolves.toBeChecked()
      await expect(
        getOfferInputForField('visualDisabilityCompliant')
      ).resolves.not.toBeChecked()
      await expect(
        getOfferInputForField('motorDisabilityCompliant')
      ).resolves.toBeChecked()
      await expect(
        getOfferInputForField('mentalDisabilityCompliant')
      ).resolves.toBeChecked()
    })

    it('should not send not editable fields for non-synchronised offers', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          isbn: '1234567890123',
        },
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      await waitFor(() =>
        expect(pcapi.updateOffer).toHaveBeenCalledWith(
          editedOffer.id,
          expect.not.objectContaining({
            venueId: expect.anything(),
            type: expect.anything(),
          })
        )
      )
    })

    it('should show a success notification when form was correctly submitted', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          isbn: '1234567890123',
        },
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      await renderOffers(props, store)
      const submitButton = screen.getByText('Enregistrer')

      // When
      userEvent.click(submitButton)

      // Then
      expect(submitButton).toBeDisabled()
      const successNotification = await screen.findByText(
        'Votre offre a bien été modifiée'
      )
      expect(successNotification).toBeInTheDocument()
    })

    it('should send accessibility fields for synchronized offers', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          stageDirector: 'Mr Stage Director',
        },
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        lastProvider: {
          name: 'Allociné',
        },
        status: 'ACTIVE',
      }

      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      const cinema = {
        ...categories,
        subcategories: [
          {
            ...categories.subcategories[0],
            isEvent: true,
            conditionalFields: ['author', 'visa', 'stageDirector'],
          },
        ],
      }

      pcapi.loadCategories.mockResolvedValue(cinema)

      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      await waitFor(() =>
        expect(pcapi.updateOffer).toHaveBeenCalledWith(
          editedOffer.id,
          expect.objectContaining({
            audioDisabilityCompliant: false,
            visualDisabilityCompliant: true,
            motorDisabilityCompliant: false,
            mentalDisabilityCompliant: false,
          })
        )
      )
    })

    it('should not send extraData for synchronized offers', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        extraData: {
          stageDirector: 'Mr Stage Director',
        },
        lastProvider: {
          name: 'Allociné',
        },
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      await waitFor(() =>
        expect(pcapi.updateOffer).toHaveBeenCalledWith(
          editedOffer.id,
          expect.not.objectContaining({
            extraData: null,
          })
        )
      )
    })

    it('should send null extraData when removing them', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          author: 'Mon auteur',
        },
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      await setOfferValues({ author: DEFAULT_FORM_VALUES.author })

      // Then
      userEvent.click(screen.getByText('Enregistrer'))
      await waitFor(() =>
        expect(pcapi.updateOffer).toHaveBeenCalledWith(
          editedOffer.id,
          expect.objectContaining({
            extraData: null,
          })
        )
      )
    })

    it('should remove attribute from extraData when no value is provided', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          author: 'Mon auteur',
          isbn: '123456789',
        },
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      const category = {
        ...categories,
        subcategories: [
          {
            ...categories.subcategories[0],
            conditionalFields: ['author', 'isbn'],
          },
        ],
      }

      pcapi.loadCategories.mockResolvedValue(category)

      await renderOffers(props, store)

      // When
      await setOfferValues({ author: DEFAULT_FORM_VALUES.author })

      // Then
      userEvent.click(screen.getByText('Enregistrer'))

      await waitFor(() =>
        expect(pcapi.updateOffer).toHaveBeenCalledWith(
          editedOffer.id,
          expect.objectContaining({
            extraData: { isbn: editedOffer.extraData.isbn },
          })
        )
      )
    })

    it('should remove notification email when remove the will to receive notifications', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: {
          isbn: '1234567890123',
        },
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      await renderOffers(props, store)
      await setOfferValues({ receiveNotificationEmails: false })

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      await waitFor(() =>
        expect(pcapi.updateOffer).toHaveBeenCalledWith(
          editedOffer.id,
          expect.objectContaining({
            bookingEmail: null,
          })
        )
      )
    })

    it('should show error for email notification input when asking to receive booking emails and no email was provided', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: null,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      await renderOffers(props, store)
      await setOfferValues({ receiveNotificationEmails: true })
      fireEvent.change(
        screen.getByLabelText('Email auquel envoyer les notifications :'),
        {
          target: { value: '' },
        }
      )

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const bookingEmailInput = await findInputErrorForField('bookingEmail')
      expect(bookingEmailInput).toHaveTextContent('Ce champ est obligatoire')
      expect(
        screen.getByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )
      ).toBeInTheDocument()
    })

    it('should show error sent by API and show an error notification', async () => {
      // Given
      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
        extraData: {
          isbn: '1234567890123',
        },
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      pcapi.updateOffer.mockRejectedValue({
        errors: { name: "Ce nom n'est pas valide" },
      })
      await renderOffers(props, store)
      await setOfferValues({ name: 'Ce nom serait-il invalide ?' })

      // When
      userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const nameError = await screen.findByText("Ce nom n'est pas valide")
      expect(nameError).toBeInTheDocument()
      const errorNotification = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
      expect(errorNotification).toBeInTheDocument()
    })

    it('should show a success notification when a thumbnail submitted', async () => {
      // Given
      jest.spyOn(Object, 'values').mockReturnValue(['item'])
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      pcapi.updateOffer.mockResolvedValue({ id: 'AA' })
      pcapi.postThumbnail.mockResolvedValue({ id: 'BB' })
      await renderOffers(props, store)

      // When
      fireEvent.click(screen.getByText('Enregistrer'))

      // Then
      const successNotification = await screen.findByText(
        'Votre offre a bien été modifiée'
      )
      expect(successNotification).toBeInTheDocument()
    })
  })

  describe('when clicking on cancel link', () => {
    it('should call computeOffersUrl with proper params', async () => {
      // Given
      const testStore = {
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
          },
        },
      }
      store = configureTestStore(testStore)

      const editedOffer = {
        id: 'ABC12',
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: 'booking@example.net',
        extraData: null,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)
      await renderOffers(props, store)

      // When
      userEvent.click(screen.getByRole('link', { name: 'Annuler et quitter' }))

      // Then
      expect(computeUrl.computeOffersUrl).toHaveBeenLastCalledWith(
        testStore.offers.searchFilters,
        1
      )
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
        nonHumanizedId: 111,
        subcategoryId: 'ID',
        name: 'My edited offer',
        description: 'Offer description',
        venueId: editedOfferVenue.id,
        venue: editedOfferVenue,
        withdrawalDetails: 'Offer withdrawal details',
        bookingEmail: null,
        status: 'ACTIVE',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(editedOffer)

      // When
      await renderOffers(props, store)

      // Then
      const cancelLink = screen.getByRole('link', {
        name: 'Annuler et quitter',
      })
      expect(cancelLink).toBeInTheDocument()
      expect(cancelLink).toHaveAttribute('href', '/offres')
    })
  })
})
