import '@testing-library/jest-dom'

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import { OFFER_WITHDRAWAL_TYPE_OPTIONS } from 'core/Offers'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { loadFakeApiCategories } from 'utils/fakeApi'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import OfferLayout from '../../OfferLayout'

import {
  findInputErrorForField,
  getOfferInputForField,
  queryInputErrorForField,
  setOfferValues,
  sidebarDisplayed,
} from './helpers'

Element.prototype.scrollIntoView = () => {}

jest.mock('repository/pcapi/pcapi', () => ({
  ...jest.requireActual('repository/pcapi/pcapi'),
  createOffer: jest.fn(),
  getUserValidatedOfferersNames: jest.fn(),
  getVenue: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadCategories: jest.fn(),
  loadStocks: jest.fn(),
  loadTypes: jest.fn(),
  postThumbnail: jest.fn(),
}))

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn().mockReturnValue(false),
}))

const renderOffers = async (props, store, queryParams = null) => {
  const rtlRenderReturn = render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          { pathname: '/offre/creation/individuel', search: queryParams },
        ]}
      >
        <Route
          path={[
            '/offre/creation/individuel',
            '/offre/:offerId([A-Z0-9]+)/individuel',
          ]}
        >
          <>
            <OfferLayout {...props} />
            <NotificationContainer />
          </>
        </Route>
      </MemoryRouter>
    </Provider>
  )
  await getOfferInputForField('categoryId')

  return rtlRenderReturn
}

describe('offerDetails - Creation - pro user', () => {
  let offerers
  let props
  let store
  let venues

  beforeEach(() => {
    store = configureTestStore({
      features: {
        initialized: true,
        list: [
          {
            isActive: true,
            name: 'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION',
            nameKey: 'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION',
          },
        ],
      },
      user: {
        currentUser: {
          publicName: 'François',
          isAdmin: false,
          email: 'francois@example.com',
        },
      },
    })
    props = {
      setShowThumbnailForm: jest.fn(),
    }
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
        bookingEmail: 'lieu@example.com',
        withdrawalDetails: 'Modalité retrait 1',
      },
      {
        id: 'ABC',
        isVirtual: false,
        managingOffererId: offerer2Id,
        name: "L'autre lieu",
        offererName: "L'autre structure",
        bookingEmail: 'autre-lieu@example.com',
        withdrawalDetails: 'Modalité retrait 2',
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
      },
      {
        id: 'ABCD',
        isVirtual: true,
        managingOffererId: offerer2Id,
        name: "L'autre lieu (Offre numérique)",
        offererName: "L'autre structure",
        withdrawalDetails: null,
      },
      {
        id: 'ABCDE',
        isVirtual: true,
        managingOffererId: offerer2Id,
        name: "L'autre lieu du lieu",
        offererName: "L'autre structure",
        publicName: "Le nom d'usage de l'autre autre lieu",
        withdrawalDetails: 'Modalité retrait 3',
      },
    ]

    pcapi.getUserValidatedOfferersNames.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
    pcapi.getVenue.mockReturnValue(Promise.resolve())
    pcapi.createOffer.mockResolvedValue({})
    loadFakeApiCategories()
    jest.spyOn(window, 'scrollTo').mockImplementation()
  })

  describe('render when creating a new offer as pro user', () => {
    it('should get categories from API', async () => {
      // When
      await renderOffers(props, store)

      // FIXME : we query categories when we render OfferLayout or OfferDetails.
      // I think we should query load categories only once but i'm too afraid to
      // break everything now
      // (mageoffray 04-07-22)
      await waitFor(() => expect(pcapi.loadCategories).toHaveBeenCalledTimes(2))
    })

    it("should get user's offerer from API", async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(pcapi.getUserValidatedOfferersNames).toHaveBeenCalledTimes(1)
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
      expect(
        screen.getByText('Type d’offre', { selector: '.section-title' })
      ).toBeInTheDocument()
    })

    it('should not display a placeholder for preview', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(
        screen.queryByText('Ajouter une image', { selector: 'button' })
      ).not.toBeInTheDocument()
    })

    it('should only display digital categories and subcategories', async () => {
      //Given
      const queryParams = `?structure=${offerers[0].id}&lieu=${venues[0].id}&numerique`

      //When
      await renderOffers(props, store, queryParams)

      //Then
      expect(
        screen.queryByText('Beaux-arts', { selector: 'option' })
      ).not.toBeInTheDocument()
      await setOfferValues({ categoryId: 'FILM' })
      expect(
        screen.queryByText('Support physique', { selector: 'option' })
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
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'LIVRE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'LIVRE_PAPIER'
          )

          // Then
          expect(
            screen.getByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).toBeInTheDocument()
          expect(
            screen.getByRole('link', { name: '+ Ajouter un lieu' })
          ).toHaveAttribute('href', '/structures//lieux/creation')
          expect(
            screen.queryByLabelText('Type de spectacle')
          ).not.toBeInTheDocument()
        })

        it('should not inform user about venue creation if at least one non virtual venue', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // Then
          expect(
            screen.queryByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).not.toBeInTheDocument()
          expect(
            screen.queryByRole('link', { name: '+ Ajouter un lieu' })
          ).not.toBeInTheDocument()
          await expect(
            screen.findByLabelText('Genre musical', { exact: false })
          ).resolves.toBeInTheDocument()
        })
      })

      describe('when selecting ONLINE category', () => {
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
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'LIVESTREAM_MUSIQUE'
          )

          // Then
          expect(
            screen.queryByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).not.toBeInTheDocument()
          expect(
            screen.queryByRole('link', { name: '+ Ajouter un lieu' })
          ).not.toBeInTheDocument()
        })

        it("should pre-fill booking notification email field with user's email", async () => {
          // Given
          venues = [
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
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'LIVESTREAM_MUSIQUE'
          )

          // When
          await userEvent.click(
            screen.getByLabelText(/Être notifié par email des réservations/)
          )

          // Then
          expect(
            screen.getByLabelText('Email auquel envoyer les notifications :')
              .value
          ).toBe('francois@example.com')
        })
      })

      describe('when selecting ONLINE_OR_OFFLINE category', () => {
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
          ]
          pcapi.getVenuesForOfferer.mockResolvedValue(venues)
          pcapi.getVenue.mockResolvedValue(venues[0])
          await renderOffers(props, store)

          // When
          await setOfferValues({ categoryId: 'MUSEE' })
          await setOfferValues({ subcategoryId: 'VISITE_GUIDEE' })
          await sidebarDisplayed()

          // Then
          expect(
            screen.queryByText(
              'Pour créer une offre de ce type, ajoutez d’abord un lieu à l’une de vos structures.'
            )
          ).not.toBeInTheDocument()
          expect(
            screen.queryByRole('link', { name: '+ Ajouter un lieu' })
          ).not.toBeInTheDocument()
        })
      })

      it('should display a placeholder for the offer thumbnail', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'CINEMA'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'SEANCE_CINE'
        )

        // Then
        expect(
          screen.getByText('Ajouter une image', { selector: 'button' })
        ).toBeInTheDocument()
      })

      describe('offer preview', () => {
        it('should display title when input is filled', async () => {
          // given
          await renderOffers(props, store)
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'CINEMA'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'SEANCE_CINE'
          )

          // when
          const titleInput = await screen.findByLabelText("Titre de l'offre", {
            exact: false,
          })
          await userEvent.type(titleInput, 'Mon joli titre')

          // then
          expect(screen.getByTestId('offer-preview-section')).toHaveTextContent(
            'Mon joli titre'
          )
        })

        it('should display description when input is filled', async () => {
          // given
          await renderOffers(props, store)
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'CINEMA'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'SEANCE_CINE'
          )

          // when
          const descriptionInput = await screen.findByLabelText('Description', {
            exact: false,
          })
          await userEvent.type(descriptionInput, 'Ma jolie description')

          // then
          expect(screen.getByTestId('offer-preview-section')).toHaveTextContent(
            'Ma jolie description'
          )
        })

        it('should display terms of withdrawal when input is filled', async () => {
          // given
          await renderOffers(props, store)
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'CINEMA'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'SEANCE_CINE'
          )
          // when

          await userEvent.type(
            await screen.findByLabelText(/Informations de retrait/),
            'Mes jolies modalités'
          )

          // then
          expect(screen.getByTestId('offer-preview-section')).toHaveTextContent(
            'Modalités de retrait'
          )
        })

        it("should display disabled 'isDuo' icon for offers that aren't event", async () => {
          await renderOffers(props, store)
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'LIVRE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'LIVRE_PAPIER'
          )
          const disabledisDuoBox = await screen.findByText('À deux !', {
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
              await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
              await setOfferValues({ subcategoryId: 'CONCERT' })
              await setOfferValues({
                offererId: offererWithMultipleVenues.id,
              })

              // When
              await userEvent.selectOptions(
                await screen.findByLabelText('Lieu'),
                physicalVenue.id
              )
              await sidebarDisplayed()

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(within(offerPreview).getByText('Où ?')).toBeInTheDocument()
              expect(
                within(offerPreview).getByText('Adresse')
              ).toBeInTheDocument()
              expect(
                within(offerPreview).getByText('Distance')
              ).toBeInTheDocument()
            })

            it("should display venue's public name if provided", async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              physicalVenue.publicName = 'Le petit nom du lieu'
              pcapi.getVenue.mockResolvedValue(physicalVenue)
              await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
              await setOfferValues({ subcategoryId: 'CONCERT' })
              await setOfferValues({
                offererId: offererWithMultipleVenues.id,
              })

              // When
              await userEvent.selectOptions(
                await screen.findByLabelText('Lieu'),
                physicalVenue.id
              )
              await sidebarDisplayed()

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(
                within(offerPreview).getByText(physicalVenue.publicName, {
                  exact: false,
                })
              ).toBeInTheDocument()
              expect(
                within(offerPreview).queryByText(physicalVenue.name, {
                  exact: false,
                })
              ).not.toBeInTheDocument()
            })

            it("should display venue's name if public name not provided", async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              pcapi.getVenue.mockResolvedValue(physicalVenue)
              await userEvent.selectOptions(
                await screen.findByLabelText(/Catégorie/),
                'MUSIQUE_LIVE'
              )
              await userEvent.selectOptions(
                await screen.findByLabelText(/Sous-catégorie/),
                'CONCERT'
              )
              await userEvent.selectOptions(
                await screen.findByLabelText(/Structure/),
                offererWithMultipleVenues.id
              )

              // When
              await userEvent.selectOptions(
                await screen.findByLabelText(/Lieu/),
                physicalVenue.id
              )
              await sidebarDisplayed()

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(
                within(offerPreview).getByText(physicalVenue.name, {
                  exact: false,
                })
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
              await userEvent.selectOptions(
                await screen.findByLabelText(/Catégorie/),
                'MUSIQUE_LIVE'
              )
              await userEvent.selectOptions(
                await screen.findByLabelText(/Sous-catégorie/),
                'CONCERT'
              )
              await userEvent.selectOptions(
                await screen.findByLabelText(/Structure/),
                offererWithMultipleVenues.id
              )

              // When
              await userEvent.selectOptions(
                await screen.findByLabelText(/Lieu/),
                physicalVenue.id
              )
              await sidebarDisplayed()

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              const expectedFormattedAddress = `${physicalVenue.name} - ${physicalVenue.address} - ${physicalVenue.postalCode} - ${physicalVenue.city}`
              expect(
                within(offerPreview).getByText(expectedFormattedAddress)
              ).toBeInTheDocument()
            })
          })

          describe('when virtual venue is selected', () => {
            it('should not display "Où" section', async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const virtualVenue = venues[2]
              pcapi.getVenue.mockResolvedValue(virtualVenue)
              await userEvent.selectOptions(
                await screen.findByLabelText(/Catégorie/),
                'JEU'
              )
              await userEvent.selectOptions(
                await screen.findByLabelText(/Sous-catégorie/),
                'RENCONTRE_JEU'
              )

              await setOfferValues({
                offererId: offererWithMultipleVenues.id,
              })

              // When
              await setOfferValues({ venueId: virtualVenue.id })
              await sidebarDisplayed()

              // Then
              const offerPreview = screen.getByTestId('offer-preview-section')
              expect(
                within(offerPreview).queryByText('Où ?')
              ).not.toBeInTheDocument()
              expect(
                within(offerPreview).queryByText('Adresse')
              ).not.toBeInTheDocument()
              expect(
                within(offerPreview).queryByText('Distance')
              ).not.toBeInTheDocument()
            })
          })

          describe('when no venue is selected', () => {
            it('should not display "Où" section', async () => {
              // Given
              await renderOffers(props, store)
              const offererWithMultipleVenues = offerers[1]
              const physicalVenue = venues[1]
              await userEvent.selectOptions(
                await screen.findByLabelText(/Catégorie/),
                'MUSIQUE_LIVE'
              )
              await userEvent.selectOptions(
                await screen.findByLabelText(/Sous-catégorie/),
                'CONCERT'
              )

              pcapi.getVenue.mockReturnValue(venues[0])
              await userEvent.selectOptions(
                await screen.findByLabelText(/Structure/),
                offererWithMultipleVenues.id
              )

              // When
              pcapi.getVenue.mockReturnValue(physicalVenue)
              await userEvent.selectOptions(
                await screen.findByLabelText(/Lieu/),
                physicalVenue.id
              )
              await sidebarDisplayed()
              await userEvent.selectOptions(
                await screen.findByLabelText(/Lieu/),
                ''
              )
              // Then
              expect(screen.getByTestId('offer-preview-section')).not.toContain(
                'Adresse'
              )
            })
          })
        })
      })

      it('should display "Infos pratiques", "Infos artistiques", "Accessibilité", "Lien pour le grand public" and "Notification" section', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'MUSIQUE_LIVE'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'CONCERT'
        )

        // Then
        expect(
          screen.getByRole('heading', {
            name: 'Informations artistiques',
            level: 3,
          })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('heading', {
            name: 'Informations pratiques',
            level: 3,
          })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('heading', { name: 'Accessibilité', level: 3 })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('heading', {
            name: 'Lien pour le grand public',
            level: 3,
          })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('heading', { name: 'Notifications', level: 3 })
        ).toBeInTheDocument()
      })

      it('should display "Autres caractéristiques" section if offer can be duo or educational', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'MUSIQUE_LIVE'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'CONCERT'
        )

        // Then
        expect(
          screen.getByRole('heading', {
            name: 'Autres caractéristiques',
            level: 3,
          })
        ).toBeInTheDocument()
      })

      it('should not display "Autres caractéristiques" section if offer cannot be duo nor educational', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'MEDIA'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'ARTICLE_PRESSE'
        )

        // Then
        expect(
          screen.queryByRole('heading', {
            name: 'Autres caractéristiques',
            level: 3,
          })
        ).not.toBeInTheDocument()
      })

      it('should display email notification input when asking to receive booking emails', async () => {
        // Given
        await renderOffers(props, store)
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'MUSIQUE_LIVE'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'CONCERT'
        )

        // When
        await userEvent.click(
          screen.getByLabelText(/Être notifié par email des réservations/)
        )

        // Then
        const bookingEmailInput = screen.getByLabelText(
          'Email auquel envoyer les notifications :'
        )
        expect(bookingEmailInput).toBeInTheDocument()
      })

      it('should display email notification input errors when email is wrong or missing', async () => {
        // Given
        const queryParams = `?structure=${offerers[1].id}&lieu=${venues[1].id}`
        pcapi.getVenue.mockResolvedValue(venues[1])
        await renderOffers(props, store, queryParams)
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'BEAUX_ARTS'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'MATERIEL_ART_CREATIF'
        )
        await userEvent.click(screen.getByLabelText(/Titre de l'offre/))
        await userEvent.paste('Titre')
        await userEvent.click(
          screen.getByLabelText(/Être notifié par email des réservations/)
        )

        // no email
        const bookingEmailInput = screen.getByLabelText(
          'Email auquel envoyer les notifications :'
        )
        await userEvent.clear(bookingEmailInput)
        await userEvent.click(screen.getByText('Étape suivante'))
        expect(
          screen.getByText('Ce champ est obligatoire.')
        ).toBeInTheDocument()

        // wrong email
        await userEvent.click(bookingEmailInput)
        await userEvent.paste('wrong email')
        await userEvent.click(screen.getByText('Étape suivante'))
        expect(
          screen.getByText('Veuillez renseigner un email valide')
        ).toBeInTheDocument()
      })

      it('should display a text input for an external ticket office url"', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await userEvent.selectOptions(
          await screen.findByLabelText(/Catégorie/),
          'MUSIQUE_LIVE'
        )
        await userEvent.selectOptions(
          await screen.findByLabelText(/Sous-catégorie/),
          'CONCERT'
        )

        // Then
        const externalTicketOfficeUrlInput = await getOfferInputForField(
          'externalTicketOfficeUrl'
        )
        expect(externalTicketOfficeUrlInput).toBeInTheDocument()
      })

      describe('accessibility fields', () => {
        it('should display accessibility section description', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )

          // Then
          expect(
            screen.getByText(
              'Cette offre est-elle accessible aux publics en situation de handicaps :'
            )
          ).toBeInTheDocument()
        })
      })

      describe('venue selection', () => {
        it('should display an offerer selection and a venue selection when user is pro', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )

          // Then
          expect(screen.queryByLabelText('Structure')).toBeInTheDocument()
          const venueInput = screen.queryByLabelText('Lieu')
          expect(venueInput).toBeInTheDocument()
          expect(venueInput).not.toHaveAttribute('disabled')
        })

        it('should have offerer selected when given as queryParam and filter venues', async () => {
          // Given
          pcapi.getVenue.mockResolvedValue(venues[0])
          await renderOffers(props, store, `?structure=${offerers[0].id}`)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )
          await sidebarDisplayed()

          // Then
          expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
          expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
          expect(
            screen.queryByDisplayValue(venues[1].name)
          ).not.toBeInTheDocument()
          expect(
            screen.queryByDisplayValue(venues[2].name)
          ).not.toBeInTheDocument()
        })

        it('should select offerer when there is only one option', async () => {
          // Given
          pcapi.getUserValidatedOfferersNames.mockResolvedValue([offerers[0]])
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )

          // Then
          expect(screen.getByDisplayValue(offerers[0].name)).toBeInTheDocument()
        })

        it('should have venue selected when given as queryParam', async () => {
          // Given
          pcapi.getVenue.mockResolvedValue(venues[0])
          await renderOffers(
            props,
            store,
            `?lieu=${venues[0].id}&structure=${venues[0].managingOffererId}`
          )

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )
          await sidebarDisplayed()

          // Then
          expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
        })

        it('should select venue when there is only one option', async () => {
          // Given
          pcapi.getVenuesForOfferer.mockResolvedValue([venues[0]])
          pcapi.getVenue.mockResolvedValue(venues[0])
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )
          await sidebarDisplayed()

          // Then
          expect(screen.getByDisplayValue(venues[0].name)).toBeInTheDocument()
        })

        it('should select virtual venue and disable the input when offer subcategory is online only', async () => {
          // Given
          pcapi.getVenuesForOfferer.mockResolvedValue([venues[2]])
          pcapi.getVenue.mockResolvedValue(venues[2])
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MEDIA'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'ABO_PRESSE_EN_LIGNE'
          )

          // Then
          expect(screen.getByText(venues[2].name)).toBeInTheDocument()
          expect(
            screen.getByText(venues[2].name).closest('select')
          ).toBeDisabled()
        })

        it('should only display physical venues when offer type is offline only', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )

          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[1].name)).toBeInTheDocument()
          expect(screen.queryByText(venues[2].name)).not.toBeInTheDocument()
        })

        it('should display all venues when offer type is offline and online', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'JEU'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'RENCONTRE_JEU'
          )

          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[1].name)).toBeInTheDocument()
          expect(screen.getByText(venues[2].name)).toBeInTheDocument()
        })

        it('should only display venues of selected offerer', async () => {
          // Given
          await renderOffers(props, store)

          // When
          pcapi.getVenue.mockReturnValue(venues[0])
          await setOfferValues({
            categoryId: 'MUSIQUE_LIVE',
            subcategoryId: 'CONCERT',
            offererId: offerers[0].id,
          })

          await sidebarDisplayed()
          const offerPreview = screen.getByTestId('offer-preview-section')

          // Then
          expect(
            within(offerPreview).getByText(venues[0].name)
          ).toBeInTheDocument()
          expect(
            within(offerPreview).queryByText(venues[1].name)
          ).not.toBeInTheDocument()
          expect(
            within(offerPreview).queryByText(venues[2].name)
          ).not.toBeInTheDocument()
        })

        it('should display all venues when unselecting offerer', async () => {
          // Given
          await renderOffers(props, store)
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'FESTIVAL_MUSIQUE'
          )
          pcapi.getVenue.mockReturnValue(venues[0])

          await userEvent.selectOptions(
            await screen.findByLabelText(/Structure/),
            offerers[0].id
          )
          await sidebarDisplayed()

          // When
          await userEvent.selectOptions(screen.getByLabelText(/Structure/), '')

          // Then
          // 5 children = Sélectionner un lieu + 4 lieux
          expect(screen.getByLabelText(/Lieu/).children).toHaveLength(5)
        })

        it('should select offerer of selected venue', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // When
          pcapi.getVenue.mockReturnValue(venues[0])
          await setOfferValues({ venueId: venues[0].id })
          await sidebarDisplayed()

          // Then
          expect(screen.getByLabelText('Structure')).toHaveDisplayValue(
            offerers[0].name
          )
        })

        it('should warn user if selected offerer has no physical venues but physical type is selected', async () => {
          // Given
          const venuesForOfferer = [
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
          pcapi.getVenuesForOfferer.mockResolvedValue(venuesForOfferer)
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // When
          await setOfferValues({ offererId: offerers[0].id })
          await sidebarDisplayed()

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

          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'CONCERT'
          )
          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Structure/),
            offerers[0].id
          )
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
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // When
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'LIVESTREAM_MUSIQUE' })

          // Then
          await waitFor(() =>
            expect(screen.getByLabelText('Lieu')).toBeInTheDocument()
          )
          const venueIdError = queryInputErrorForField('venueId')
          expect(venueIdError).toBeNull()
        })

        it('should only display venues from active offerers', async () => {
          // when
          await renderOffers(props, store)

          // then
          expect(pcapi.getVenuesForOfferer).toHaveBeenCalledWith({
            activeOfferersOnly: true,
          })
        })

        it('should display venues publicName instead of name if exists', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'JEU'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'RENCONTRE_JEU'
          )
          // Then
          expect(screen.getByText(venues[0].name)).toBeInTheDocument()
          expect(screen.getByText(venues[1].name)).toBeInTheDocument()
          expect(screen.getByText(venues[2].name)).toBeInTheDocument()
          expect(screen.queryByText(venues[3].name)).not.toBeInTheDocument()
          expect(screen.getByText(venues[3].publicName)).toBeInTheDocument()
        })
      })

      describe('with conditional fields', () => {
        describe('"musicType"', () => {
          it('should display a music type selection', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
            await setOfferValues({ subcategoryId: 'CONCERT' })

            // Then
            const musicTypeInput = await getOfferInputForField('musicType')
            expect(musicTypeInput).toBeInTheDocument()
          })

          it('should display a music subtype selection when a musicType is selected', async () => {
            // Given
            await renderOffers(props, store)
            await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
            await setOfferValues({ subcategoryId: 'CONCERT' })

            // When
            await setOfferValues({ musicType: '501' })

            // Then
            const musicSubTypeInput = await getOfferInputForField(
              'musicSubType'
            )
            expect(musicSubTypeInput).toBeInTheDocument()
          })

          it('should not display a music type selection when changing to an offer type wihtout "musicType" conditional field', async () => {
            // Given
            await renderOffers(props, store)
            await userEvent.selectOptions(
              await screen.findByLabelText(/Catégorie/),
              'MUSIQUE_LIVE'
            )
            await userEvent.selectOptions(
              await screen.findByLabelText(/Sous-catégorie/),
              'CONCERT'
            )

            // When

            await userEvent.selectOptions(
              await screen.findByLabelText(/Catégorie/),
              'LIVRE'
            )
            await userEvent.selectOptions(
              await screen.findByLabelText(/Sous-catégorie/),
              'LIVRE_PAPIER'
            )

            // Then
            expect(
              screen.queryByLabelText(/Genre musical/)
            ).not.toBeInTheDocument()
          })

          it('should not display a music subtype selection when a musicType is not selected and a showType was selected before', async () => {
            // Given
            await renderOffers(props, store)
            await setOfferValues({ categoryId: 'SPECTACLE' })
            await setOfferValues({ subcategoryId: 'SPECTACLE_REPRESENTATION' })
            await setOfferValues({ showType: '1300' })
            await setOfferValues({ showSubType: '1307' })

            // When
            await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
            await setOfferValues({ subcategoryId: 'CONCERT' })

            // Then
            expect(
              screen.queryByLabelText('Sous genre', { exact: false })
            ).not.toBeInTheDocument()
          })
        })

        describe('"showType"', () => {
          it('should display a show type selection', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ categoryId: 'SPECTACLE' })
            await setOfferValues({ subcategoryId: 'SPECTACLE_REPRESENTATION' })

            // Then

            await waitFor(() =>
              expect(screen.getByLabelText(/Type/)).toBeInTheDocument()
            )
          })

          it('should display a show subtype selection when a showType is selected', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ categoryId: 'SPECTACLE' })
            await setOfferValues({ subcategoryId: 'SPECTACLE_REPRESENTATION' })
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
            await setOfferValues({ categoryId: 'CONFERENCE' })
            await setOfferValues({ subcategoryId: 'RENCONTRE' })

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
            await setOfferValues({ categoryId: 'CINEMA' })
            await setOfferValues({ subcategoryId: 'SEANCE_CINE' })

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
            await setOfferValues({ categoryId: 'CINEMA' })
            await setOfferValues({ subcategoryId: 'SEANCE_CINE' })

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
            await setOfferValues({ categoryId: 'LIVRE' })
            await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })

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
            await setOfferValues({ categoryId: 'CINEMA' })
            await setOfferValues({ subcategoryId: 'SEANCE_CINE' })

            // Then
            const stageDirectorInput = await getOfferInputForField(
              'stageDirector'
            )
            expect(stageDirectorInput).toBeInTheDocument()
          })
        })

        describe('"performer"', () => {
          it('should display a text input "Interprète"', async () => {
            // Given
            await renderOffers(props, store)

            // When
            await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
            await setOfferValues({ subcategoryId: 'CONCERT' })

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

          // When
          await setOfferValues({ categoryId: 'MEDIA' })
          await setOfferValues({ subcategoryId: 'ABO_PRESSE_EN_LIGNE' })

          // When
          pcapi.getVenue.mockResolvedValue(venues[2])
          await setOfferValues({ venueId: venues[2].id })
          await sidebarDisplayed()

          // Then
          const urlInput = await getOfferInputForField('url')
          expect(urlInput).toBeInTheDocument()
        })

        it('should display refundable banner when offer type is online only', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'MEDIA' })
          await setOfferValues({ subcategoryId: 'ABO_PRESSE_EN_LIGNE' })

          // When
          pcapi.getVenue.mockResolvedValue(venues[2])
          await setOfferValues({ venueId: venues[2].id })
          await sidebarDisplayed()

          // Then
          expect(
            screen.getByText(
              'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
            )
          ).toBeInTheDocument()
        })

        it('should remove refundable banner after selecting a refundable category', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({
            categoryId: 'MEDIA',
            subcategoryId: 'ABO_PRESSE_EN_LIGNE',
          })

          const NotRefundableBanner = await screen.findByText(
            'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
          )
          expect(NotRefundableBanner).toBeInTheDocument()

          // When
          await setOfferValues({
            categoryId: 'SPECTACLE',
            subcategoryId: 'SPECTACLE_REPRESENTATION',
          })

          // Then
          expect(NotRefundableBanner).not.toBeInTheDocument()
        })

        it('should display refundable banner when offer type is online and offline', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'FILM' })
          await setOfferValues({ subcategoryId: 'VOD' })

          // When
          pcapi.getVenue.mockResolvedValue(venues[2])
          await setOfferValues({ venueId: venues[2].id })
          await sidebarDisplayed()

          // Then
          expect(
            screen.getByText(
              'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
            )
          ).toBeInTheDocument()
        })

        it('should not display refundable banner when offer category is Livres / livre papier', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'LIVRE' })
          await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })

          // When
          await setOfferValues({ offererId: offerers[0].id })
          await sidebarDisplayed()

          // Then
          expect(
            screen.queryByText(
              'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
            )
          ).not.toBeInTheDocument()
        })

        it('should not display refundable banner when offer type is ThingType.CINEMA_CARD', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'CINEMA' })
          await setOfferValues({ subcategoryId: 'CARTE_CINE_MULTISEANCES' })

          // When
          await setOfferValues({ offererId: offerers[0].id })
          await sidebarDisplayed()

          // Then
          expect(
            screen.queryByText(
              'Cette offre numérique ne fera pas l’objet d’un remboursement. Pour plus d’informations sur les catégories éligibles au remboursement, merci de consulter les CGU.'
            )
          ).not.toBeInTheDocument()
        })

        it('should not remind withdrawal modalities', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // When
          await setOfferValues({ offererId: offerers[0].id })
          await sidebarDisplayed()

          // Then
          const withdrawalModalitiesReminder = screen.queryByText(
            'La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos CGU.'
          )
          expect(withdrawalModalitiesReminder).not.toBeInTheDocument()
        })

        it("should pre-fill booking notification email field with user's email when category is ONLINE_OR_OFFLINE", async () => {
          // Given
          await renderOffers(props, store)
          // FIXME (mageoffray, 04-07-2022)
          // we query categories when we render OfferLayout or OfferDetails.
          // I think we should load categories only once but i'm too afraid to
          // break everything now
          await waitFor(() =>
            expect(pcapi.loadCategories).toHaveBeenCalledTimes(2)
          )

          // When

          await userEvent.selectOptions(
            await screen.findByLabelText(/Catégorie/),
            'MUSIQUE_LIVE'
          )
          await userEvent.selectOptions(
            await screen.findByLabelText(/Sous-catégorie/),
            'LIVESTREAM_MUSIQUE'
          )
          await userEvent.click(
            await screen.findByLabelText(
              /Être notifié par email des réservations/
            )
          )
          await userEvent.selectOptions(
            screen.getByLabelText(/Structure/),
            offerers[0].id
          )

          // Then
          expect(
            screen.getByLabelText('Email auquel envoyer les notifications :')
              .value
          ).toBe('francois@example.com')
        })
      })

      describe('when offer type is event type', () => {
        it('should display a time input "Durée"', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // Then
          const durationInput = await getOfferInputForField('durationMinutes')
          expect(durationInput).toBeInTheDocument()
        })

        it('should not remind withdrawal modalities', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
          await setOfferValues({ subcategoryId: 'CONCERT' })

          // Then
          const withdrawalModalitiesReminder = screen.queryByText(
            'La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos CGU.'
          )
          expect(withdrawalModalitiesReminder).not.toBeInTheDocument()
        })
      })

      describe('when offer type is thing type and venue is not virtual', () => {
        it('should remind withdrawal modalities in "Informations pratiques" section', async () => {
          // Given
          await renderOffers(props, store)

          // When
          await setOfferValues({ categoryId: 'LIVRE' })
          await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })
          pcapi.getVenue.mockResolvedValue(venues[0])
          await setOfferValues({ venueId: venues[0].id })
          await sidebarDisplayed()

          // Then
          const informationsPratiquesSection = within(
            screen.getByText('Informations pratiques').closest('section')
          )
          const withdrawalModalitiesReminder =
            informationsPratiquesSection.getByText(
              'La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos CGU.'
            )
          expect(withdrawalModalitiesReminder).toBeInTheDocument()
        })

        it('should pre-fill booking notification email field with venue’s email', async () => {
          // Given
          await renderOffers(props, store)
          await setOfferValues({ categoryId: 'LIVRE' })
          await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })

          // When
          await setOfferValues({ offererId: offerers[0].id })
          await setOfferValues({ venueId: venues[0].id })
          await setOfferValues({ receiveNotificationEmails: true })

          // Then
          await waitFor(() =>
            expect(
              screen.getByLabelText('Email auquel envoyer les notifications :')
                .value
            ).toBe(venues[0].bookingEmail)
          )
        })
      })
    })

    describe('when clicking on cancel link', () => {
      it('should redirect to offers page', async () => {
        // When
        await renderOffers(props, store)

        // Then
        await expect(
          screen.findByText('Annuler et quitter', { selector: 'a' })
        ).resolves.toHaveAttribute('href', '/offres')
      })
    })

    describe('when selecting a venue with withdrawal details filled', () => {
      it("should pre-fill withdrawal informations input and preview with venue's", async () => {
        // Given
        await renderOffers(props, store)

        await setOfferValues({ categoryId: 'LIVRE' })
        await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })

        // When
        pcapi.getVenue.mockResolvedValue(venues[1])
        await setOfferValues({ venueId: venues[1].id })
        await sidebarDisplayed()

        // Then
        expect(screen.getAllByText('Modalité retrait 2')).toHaveLength(2)
      })
    })
  })

  describe('when submitting form', () => {
    beforeEach(() => {
      jest.spyOn(api, 'getOffer').mockResolvedValue({
        status: 'DRAFT',
        venue: {
          departementCode: 93,
        },
      })
      pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    })

    it('should call API with offer data', async () => {
      // Given
      pcapi.getVenue.mockReturnValue(venues[0])
      await renderOffers(props, store)
      await userEvent.selectOptions(
        await screen.findByLabelText(/Catégorie/),
        'MUSIQUE_LIVE'
      )
      await userEvent.selectOptions(
        await screen.findByLabelText(/Sous-catégorie/),
        'CONCERT'
      )
      await userEvent.click(
        await screen.findByLabelText(/Évènement sans billet/)
      )
      await userEvent.type(
        await screen.findByLabelText(/Titre de l'offre/),
        'Ma petite offre'
      )
      await userEvent.type(
        screen.getByLabelText(/Description/),
        'Pas si petite que ça'
      )
      await userEvent.selectOptions(screen.getByLabelText(/Lieu/), venues[0].id)
      await userEvent.click(screen.getByLabelText(/Visuel/))
      await userEvent.type(screen.getByLabelText(/Durée/), '1:30')
      await userEvent.type(
        screen.getByLabelText(/URL de votre site ou billetterie/),
        'http://example.net'
      )
      await userEvent.selectOptions(
        screen.getByLabelText(/Genre musical/),
        '501'
      )
      await userEvent.selectOptions(screen.getByLabelText(/Sous genre/), '502')
      await userEvent.click(screen.getByLabelText(/Aucune/))
      await userEvent.type(
        screen.getByLabelText(/Interprète/),
        'TEST PERFORMER NAME'
      )
      await userEvent.type(
        screen.getByLabelText(/Informations de retrait/),
        'À venir chercher sur place.'
      )

      await sidebarDisplayed()

      const createdOffer = {
        name: 'Ma petite offre',
        description: 'Pas si petite que ça',
        venueId: venues[0].id,
        durationMinutes: '1:30',
        isDuo: false,
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        externalTicketOfficeUrl: 'http://example.net',
        subcategoryId: 'CONCERT',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        withdrawalDetails: 'À venir chercher sur place.',
        withdrawalType: OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET,
        id: 'CREATED',
        stocks: [],
        venue: venues[0],
        status: 'ACTIVE',
        bookingEmail: null,
      }

      pcapi.createOffer.mockResolvedValue(createdOffer)
      const submitButton = screen.getByText('Étape suivante')

      // When
      await userEvent.click(submitButton)
      await screen.findByText('Créer une offre')

      // Then
      expect(submitButton).toBeDisabled()
    })

    it('should submit externalTicketOfficeUrl as null when no value was provided', async () => {
      // Given
      const offerValues = {
        name: 'Ma petite offre',
        subcategoryId: 'LIVESTREAM_MUSIQUE',
        venueId: venues[2].id,
        extraData: {
          musicType: '501',
          musicSubType: '502',
        },
        url: 'http://www.url.com',
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      await renderOffers(props, store)

      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: 'LIVESTREAM_MUSIQUE' })
      pcapi.getVenue.mockResolvedValue(venues[2])
      await setOfferValues(offerValues)
      await sidebarDisplayed()

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      // Then
      await waitFor(() => {
        expect(pcapi.createOffer).toHaveBeenCalledWith(
          expect.objectContaining({
            externalTicketOfficeUrl: null,
          })
        )
      })
    })

    it('should redirect to stock page when form was correctly submitted', async () => {
      // Given
      const offerValues = {
        name: 'Ma petite offre',
        description: 'Pas si petite que ça',
        subcategoryId: 'LIVESTREAM_MUSIQUE',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        venueId: venues[2].id,
        url: 'http://www.url.com',
        withdrawalDetails: 'À venir chercher sur place.',
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      const createdOffer = {
        ...offerValues,
        id: 'CREATED',
        stocks: [],
        venue: venues[0],
        status: 'DRAFT',
      }
      pcapi.createOffer.mockResolvedValue(createdOffer)
      await renderOffers(props, store)
      jest.spyOn(api, 'getOffer').mockResolvedValue(createdOffer)

      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: offerValues.subcategoryId })
      pcapi.getVenue.mockResolvedValue(createdOffer.venue)
      await setOfferValues(offerValues)
      await sidebarDisplayed()

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      // Then
      await waitFor(() =>
        expect(
          screen.getByRole('heading', { name: 'Stocks et prix', level: 3 })
        ).toBeInTheDocument()
      )
      expect(
        screen.getByRole('heading', { name: 'Créer une offre', level: 1 })
      ).toBeInTheDocument()
    })

    it('should show errors for mandatory fields', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await userEvent.selectOptions(
        await screen.findByLabelText(/Catégorie/),
        'MUSIQUE_LIVE'
      )
      await userEvent.selectOptions(
        await screen.findByLabelText(/Sous-catégorie/),
        'LIVESTREAM_MUSIQUE'
      )

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

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
      const performerError = queryInputErrorForField('performer')
      expect(performerError).toBeNull()
      const isDuoError = queryInputErrorForField('isDuo')
      expect(isDuoError).toBeNull()
      const withdrawalDetailsError =
        queryInputErrorForField('withdrawalDetails')
      expect(withdrawalDetailsError).toBeNull()
      const bookingEmailInput = queryInputErrorForField('bookingEmail')
      expect(bookingEmailInput).toBeNull()
    })

    it('should show errors for category and subcategory fields', async () => {
      await renderOffers(props, store)

      await userEvent.click(screen.getByText('Étape suivante'))
      expect(pcapi.createOffer).not.toHaveBeenCalled()

      const categoryIdError = await findInputErrorForField('categoryId')
      expect(categoryIdError).toHaveTextContent('Ce champ est obligatoire')

      await setOfferValues({
        categoryId: 'MUSIQUE_LIVE',
        subcategoryId: '',
      })

      await userEvent.click(screen.getByText('Étape suivante'))
      expect(pcapi.createOffer).not.toHaveBeenCalled()

      await waitFor(() =>
        expect(
          screen.getByTestId('input-error-field-subcategoryId')
        ).toBeInTheDocument()
      )
    })

    it('should show an error notification when form is not valid', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: 'LIVESTREAM_MUSIQUE' })

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      // Then
      const errorNotification = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
      expect(errorNotification).toBeInTheDocument()
    })

    it('should show error for email notification input when asking to receive booking emails and no email was provided', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: 'LIVESTREAM_MUSIQUE' })
      await userEvent.click(
        await screen.findByLabelText(/Être notifié par email des réservations/)
      )

      // When
      await userEvent.clear(
        screen.getByLabelText(/Email auquel envoyer les notification/)
      )
      await userEvent.click(await screen.findByText('Étape suivante'))
      // Then

      expect(
        await screen.findByTestId('input-error-field-bookingEmail')
      ).toBeInTheDocument()
    })

    it('should show error for isbn input when creating offer of type LIVRE_PAPIER', async () => {
      // Given
      await renderOffers(props, store)

      await setOfferValues({ categoryId: 'LIVRE' })
      await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })

      await userEvent.click(
        await screen.findByLabelText(/Être notifié par email des réservations/)
      )

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      // Then
      expect(
        await screen.findByTestId('input-error-field-isbn')
      ).toBeInTheDocument()
    })

    it('should show error for external ticket office url input', async () => {
      // Given
      await renderOffers(props, store)
      await setOfferValues({ categoryId: 'FILM' })
      await setOfferValues({ subcategoryId: 'VOD' })
      await setOfferValues({ externalTicketOfficeUrl: 'NotAValidUrl' })

      await userEvent.type(
        await screen.findByLabelText(/URL de votre site ou billetterie/),
        'NotAValidUrl'
      )
      // When
      await userEvent.click(await screen.findByText('Étape suivante'))

      // Then
      expect(
        await screen.findByTestId('input-error-field-externalTicketOfficeUrl')
      ).toBeInTheDocument()
    })

    it('should show error for url input', async () => {
      // Given
      await renderOffers(props, store)

      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: 'LIVESTREAM_MUSIQUE' })

      await userEvent.selectOptions(
        await screen.findByLabelText('Lieu'),
        venues[2].id
      )
      await userEvent.type(
        await screen.findByLabelText(/URL d’accès à l’offre/),
        'NotAValidUrl'
      )

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      // Then

      expect(
        await screen.findByTestId('input-error-field-url')
      ).toBeInTheDocument()
    })

    it('should show error sent by API and show an error notification', async () => {
      // Given
      const offerValues = {
        name: 'Ce nom serait-il invalide ?',
        description: 'Pas si petite que ça',
        subcategoryId: 'CONCERT',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        venueId: venues[0].id,
        withdrawalDetails: 'À venir chercher sur place.',
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      pcapi.createOffer.mockRejectedValue({
        errors: { name: "Ce nom n'est pas valide" },
      })
      await renderOffers(props, store)

      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: 'CONCERT' })

      await userEvent.click(
        await screen.findByLabelText(/Évènement sans billet/)
      )

      pcapi.getVenue.mockResolvedValue(venues[0])
      await setOfferValues(offerValues)
      await sidebarDisplayed()

      // When
      await userEvent.click(await screen.findByText('Étape suivante'))

      // Then

      const errorNotification = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
      expect(errorNotification).toBeInTheDocument()

      expect(
        await screen.findByTestId('input-error-field-name')
      ).toBeInTheDocument()
    })

    it('should show an error notification and show error message with CGU link when product is not eligible', async () => {
      // Given
      const offerValues = {
        name: 'Les misérables',
        extraData: {
          isbn: '0123456789123',
        },
        venueId: venues[0].id,
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
      }

      pcapi.createOffer.mockRejectedValue({
        errors: { isbn: 'Ce produit n’est pas éligible au pass Culture.' },
      })
      await renderOffers(props, store)

      await setOfferValues({ categoryId: 'LIVRE' })
      await setOfferValues({ subcategoryId: 'LIVRE_PAPIER' })
      pcapi.getVenue.mockResolvedValue(venues[0])
      await setOfferValues(offerValues)
      await sidebarDisplayed()

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      const errorNotification = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
      expect(errorNotification).toBeInTheDocument()
      // Then
      const isbnError = queryByTextTrimHtml(
        screen,
        'Ce produit n’est pas éligible au pass Culture. Vous pouvez retrouver la liste des catégories de livres qui ne sont pas éligibles au pass Culture sur le lien suivant: FAQ',
        {
          selector: 'pre',
        }
      )
      expect(isbnError).toBeInTheDocument()
    })
  })

  describe('when quitting offer creation', () => {
    it('should show exit confirmation modal', async () => {
      // Given
      await renderOffers(props, store)

      // When
      await userEvent.click(await screen.findByText('Annuler et quitter'))

      // Then
      expect(
        await screen.findByText('Voulez-vous quitter la création d’offre ?')
      ).toBeInTheDocument()
    })
  })

  describe('when I arrive on offer Creation', () => {
    it('should display dropdown with categories', async () => {
      // When
      await renderOffers(props, store)

      // Then
      expect(
        await screen.findByText(
          'Musée, patrimoine, architecture, arts visuels',
          {
            selector: 'option',
          }
        )
      ).toBeInTheDocument()
    })

    it('should display dropdown with sub categories belonging to its category and are selectable', async () => {
      // Given
      await renderOffers(props, store)

      // When
      await setOfferValues({ categoryId: 'FILM' })

      // Then
      expect(
        await screen.findByText('Support physique (DVD, Bluray...)', {
          selector: 'option',
        })
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Carte cinéma illimité', { selector: 'option' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Sous-catégorie non sélectionnable', {
          selector: 'option',
        })
      ).not.toBeInTheDocument()
      expect(screen.getByLabelText('Sous-catégorie')).toBeInTheDocument()
      expect(
        screen.queryByText('Informations artistiques')
      ).not.toBeInTheDocument()
    })

    it('should display information artistique when sub category is set', async () => {
      // Given
      await renderOffers(props, store)

      // When
      await setOfferValues({ categoryId: 'FILM' })
      await setOfferValues({ subcategoryId: 'SUPPORT_PHYSIQUE_FILM' })

      // Then
      expect(
        await screen.findByText('Informations artistiques')
      ).toBeInTheDocument()
    })

    it('should automatically select the subcategory when selected category has only one subcategory', async () => {
      // Given
      await renderOffers(props, store)

      // When
      await setOfferValues({ categoryId: 'BEAUX_ARTS' })

      // Then
      expect(
        await screen.findByDisplayValue('Matériel arts créatifs')
      ).toBeInTheDocument()
    })

    it('should display musicType and musicSubType dropdown when I select right category', async () => {
      // Given
      await renderOffers(props, store)

      // When
      await setOfferValues({ categoryId: 'MUSIQUE_LIVE' })
      await setOfferValues({ subcategoryId: 'LIVESTREAM_MUSIQUE' })

      // Then
      expect(await screen.findByText('Genre musical')).toBeInTheDocument()

      await setOfferValues({ musicType: '501' })

      expect(await screen.findByText('Sous genre')).toBeInTheDocument()
    })

    it('should display showType dropdown when I select right category', async () => {
      // Given
      await renderOffers(props, store)

      // When
      await setOfferValues({ categoryId: 'SPECTACLE' })
      await setOfferValues({ subcategoryId: 'SPECTACLE_REPRESENTATION' })

      // Then
      await expect(
        getOfferInputForField('showType')
      ).resolves.toBeInTheDocument()

      await setOfferValues({ showType: '100' })

      await expect(
        getOfferInputForField('showSubType')
      ).resolves.toBeInTheDocument()
    })
  })
})
