import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  PatchOfferBodyModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  OfferIndividualContext,
  OfferIndividualContextValues,
} from 'context/OfferIndividualContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { Events } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { OfferIndividual, OfferSubCategory } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { AccessiblityEnum } from 'core/shared'
import { OfferIndividualVenue } from 'core/Venue/types'
import * as useAnalytics from 'hooks/useAnalytics'
import * as pcapi from 'repository/pcapi/pcapi'
import * as utils from 'screens/OfferIndividual/Informations/utils'
import { individualStockFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { InformationsProps, Informations as InformationsScreen } from '..'

const mockLogEvent = vi.fn()

vi.mock('screens/OfferIndividual/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

window.matchMedia = vi.fn().mockReturnValue({ matches: true })

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

const renderInformationsScreen = (
  props: InformationsProps,
  contextOverride: Partial<OfferIndividualContextValues>,
  features: { list: { isActive: true; nameKey: string }[] } = { list: [] }
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    features: features,
  }
  const contextValue: OfferIndividualContextValues = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={
            <OfferIndividualContext.Provider value={contextValue}>
              <InformationsScreen {...props} />
            </OfferIndividualContext.Provider>
          }
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={<div>There is the stock route content</div>}
        />
        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={<div>There is the summary route content</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
      ],
    }
  )
}

const scrollIntoViewMock = vi.fn()

describe('screens:OfferIndividual::Informations:edition', () => {
  let props: InformationsProps
  let contextOverride: Partial<OfferIndividualContextValues>
  let offer: OfferIndividual
  let subCategories: OfferSubCategory[]
  const offererId = 1
  const physicalVenueId = 1
  const virtualVenueId = 2
  const offerId = 12

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const categories = [
      {
        id: 'CID',
        proLabel: 'Catégorie CID',
        isSelectable: true,
      },
    ]
    subCategories = [
      {
        id: 'SCID virtual',
        categoryId: 'CID',
        proLabel: 'Sous catégorie online de CID',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'SCID physical',
        categoryId: 'CID',
        proLabel: 'Sous catégorie offline de CID',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    const venue: OfferIndividualVenue = {
      id: physicalVenueId,
      name: 'Venue name',
      isVirtual: false,
      accessibility: {
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.NONE]: true,
      },
      managingOffererId: 1,
      withdrawalDetails: '',
      hasMissingReimbursementPoint: false,
      hasCreatedOffer: true,
    }

    offer = {
      id: offerId,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isActive: true,
      isDuo: false,
      isEvent: true,
      isDigital: false,
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      isNational: false,
      name: 'Offer name',
      musicSubType: '',
      musicType: '',
      offererId: 12,
      offererName: '',
      performer: 'Offer performer',
      ean: '',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'SCID physical',
      image: undefined,
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      venueId: 1,
      venue: {
        id: 1,
        name: 'Venue name',
        publicName: 'Venue publicName',
        isVirtual: false,
        address: '15 rue de la corniche',
        postalCode: '75001',
        city: 'Paris',
        offerer: {
          id: 1,
          name: 'Offerer name',
        },
        departmentCode: '75',
        accessibility: {
          [AccessiblityEnum.AUDIO]: false,
          [AccessiblityEnum.MENTAL]: false,
          [AccessiblityEnum.MOTOR]: false,
          [AccessiblityEnum.VISUAL]: false,
          [AccessiblityEnum.NONE]: true,
        },
      },
      visa: '',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      stocks: [],
      lastProviderName: null,
      lastProvider: null,
      status: OfferStatus.ACTIVE,
    }

    contextOverride = {
      offerId: offer.id,
      offer: offer,
      venueList: [
        venue,
        {
          id: virtualVenueId,
          name: 'Lieu online BB',
          managingOffererId: 1,
          isVirtual: true,
          withdrawalDetails: '',
          accessibility: {
            visual: false,
            mental: false,
            audio: false,
            motor: false,
            none: true,
          },
          hasMissingReimbursementPoint: false,
          hasCreatedOffer: true,
        },
      ],
      offererNames: [{ id: offererId, name: 'Offerer name' }],
      categories,
      subCategories,
    }

    props = {
      venueId: physicalVenueId.toString(),
      offererId: offererId.toString(),
    }

    vi.spyOn(utils, 'filterCategories')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .mockImplementation((c, s, _v) => [c, s])
    vi.spyOn(api, 'patchOffer').mockResolvedValue({
      id: offerId,
    } as GetIndividualOfferResponseModel)
    vi.spyOn(api, 'postOffer').mockResolvedValue({
      id: offerId,
    } as GetIndividualOfferResponseModel)
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'deleteThumbnail').mockResolvedValue()
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should submit minimal physical offer and redirect to summary', async () => {
    renderInformationsScreen(props, contextOverride)
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.clear(nameField)
    await userEvent.type(nameField, 'Le nom de mon offre édité')

    await userEvent.click(
      await screen.findByText('Enregistrer les modifications')
    )

    expect(api.patchOffer).toHaveBeenCalledTimes(1)
    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, {
      audioDisabilityCompliant: true,
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      externalTicketOfficeUrl: 'https://external.example.com',
      extraData: {
        author: 'Offer author',
        musicSubType: '',
        musicType: '',
        performer: 'Offer performer',
        ean: '',
        showSubType: '',
        showType: '',
        speaker: 'Offer speaker',
        stageDirector: 'Offer stageDirector',
        visa: '',
      },
      isDuo: false,
      isNational: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      name: 'Le nom de mon offre édité',
      url: 'https://offer.example.com',
      visualDisabilityCompliant: true,
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      shouldSendMail: false,
    })
    expect(api.getOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('There is the summary route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should submit minimal virtual offer and redirect to summary', async () => {
    contextOverride.offer = {
      ...offer,
      venueId: virtualVenueId,
      subcategoryId: 'SCID virtual',
      isEvent: false,
      withdrawalDelay: undefined,
      withdrawalType: null,
    }
    props = {
      venueId: virtualVenueId.toString(),
      offererId: offererId.toString(),
    }

    renderInformationsScreen(props, contextOverride)
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.clear(nameField)
    await userEvent.type(nameField, 'Le nom de mon offre édité')

    await userEvent.click(
      await screen.findByText('Enregistrer les modifications')
    )

    expect(api.patchOffer).toHaveBeenCalledTimes(1)
    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, {
      audioDisabilityCompliant: true,
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      externalTicketOfficeUrl: 'https://external.example.com',
      extraData: {
        author: 'Offer author',
        musicSubType: '',
        musicType: '',
        performer: 'Offer performer',
        ean: '',
        showSubType: '',
        showType: '',
        speaker: 'Offer speaker',
        stageDirector: 'Offer stageDirector',
        visa: '',
      },
      isDuo: false,
      isNational: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      name: 'Le nom de mon offre édité',
      url: 'https://offer.example.com',
      visualDisabilityCompliant: true,
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: undefined,
      withdrawalType: undefined,
      shouldSendMail: false,
    })
    expect(api.getOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('There is the summary route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should delete offer image', async () => {
    contextOverride.offer = {
      ...offer,
      image: {
        originalUrl: 'https://image.url',
        url: 'https://image.url',
        credit: 'John Do',
      },
    }
    props = {
      venueId: physicalVenueId.toString(),
      offererId: offererId.toString(),
    }
    renderInformationsScreen(props, contextOverride)
    await screen.findByRole('heading', { name: /Type d’offre/ })
    expect(
      screen.queryByRole('button', { name: /Ajouter une image/ })
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /Supprimer/ }))
    await screen.findByText('Souhaitez-vous vraiment supprimer cette image ?')
    await userEvent.click(screen.getByTestId('confirm-dialog-button-confirm'))
    expect(api.deleteThumbnail).toHaveBeenCalledWith(offer.id)
    expect(
      await screen.findByRole('button', { name: /Ajouter une image/ })
    ).toBeInTheDocument()
  })
  it('should display an error on delete offer image api failure', async () => {
    contextOverride.offer = {
      ...offer,
      image: {
        originalUrl: 'https://image.url',
        url: 'https://image.url',
        credit: 'John Do',
      },
    }
    props = {
      venueId: virtualVenueId.toString(),
      offererId: offererId.toString(),
    }

    renderInformationsScreen(props, contextOverride)
    await screen.findByRole('heading', { name: /Type d’offre/ })
    expect(
      screen.queryByRole('button', { name: /Ajouter une image/ })
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /Supprimer/ }))
    await screen.findByText('Souhaitez-vous vraiment supprimer cette image ?')

    vi.spyOn(api, 'deleteThumbnail').mockRejectedValue(undefined)

    await userEvent.click(screen.getByTestId('confirm-dialog-button-confirm'))
    expect(
      await screen.findByText(
        'Une erreur est survenue lors de la suppression de votre image.',
        { exact: false }
      )
    ).toBeInTheDocument()
    expect(api.deleteThumbnail).toHaveBeenCalledWith(offer.id)

    expect(
      screen.queryByRole('button', { name: /Ajouter une image/ })
    ).not.toBeInTheDocument()
  })

  it('should track when submitting offer', async () => {
    renderInformationsScreen(props, contextOverride)

    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.clear(nameField)
    await userEvent.type(nameField, 'Le nom de mon offre édité')

    await userEvent.click(
      await screen.findByText('Enregistrer les modifications')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: false,
        isEdition: true,
        offerId: offer.id,
        to: 'recapitulatif',
        used: 'StickyButtons',
      }
    )
  })

  it('should track when cancelling edition', async () => {
    renderInformationsScreen(props, contextOverride)

    await userEvent.click(await screen.findByText('Annuler et quitter'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: false,
        isEdition: true,
        offerId: offer.id,
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
  })

  describe('send mail on withdrawal changes', () => {
    let expectedBody: PatchOfferBodyModel
    let features: { list: { isActive: true; nameKey: string }[] }

    beforeEach(() => {
      expectedBody = {
        audioDisabilityCompliant: true,
        bookingEmail: 'booking@email.com',
        description: 'Offer description',
        durationMinutes: 140,
        externalTicketOfficeUrl: 'https://external.example.com',
        extraData: {
          author: 'Offer author',
          musicSubType: '',
          musicType: '',
          performer: 'Offer performer',
          ean: '',
          showSubType: '',
          showType: '',
          speaker: 'Offer speaker',
          stageDirector: 'Offer stageDirector',
          visa: '',
        },
        isDuo: false,
        isNational: false,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        name: 'Le nom de mon offre édité',
        url: 'https://offer.example.com',
        visualDisabilityCompliant: true,
        withdrawalDetails: 'Offer withdrawalDetails',
        withdrawalDelay: undefined,
        withdrawalType: undefined,
        shouldSendMail: false,
      }
    })

    it('should submit when user click onCancel button, but should not send mail', async () => {
      const individualStock = individualStockFactory()
      contextOverride.offer = {
        ...offer,
        venueId: virtualVenueId,
        subcategoryId: 'SCID virtual',
        isEvent: false,
        stocks: [individualStock],
      }
      props = {
        venueId: virtualVenueId.toString(),
        offererId: offererId.toString(),
      }
      expectedBody.withdrawalDelay = 140
      expectedBody.withdrawalType = WithdrawalTypeEnum.ON_SITE

      renderInformationsScreen(props, contextOverride, features)

      const nameField = screen.getByLabelText('Titre de l’offre')
      await userEvent.clear(nameField)
      await userEvent.type(nameField, 'Le nom de mon offre édité')

      const withdrawalDetailsField = await screen.getByDisplayValue(
        'Offer withdrawalDetails'
      )
      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )
      expectedBody.withdrawalDetails = 'Nouvelle information de retrait'
      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })
      const submitButton = await screen.findByText(
        'Enregistrer les modifications'
      )

      await userEvent.click(submitButton)

      expect(
        await screen.findByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).toBeInTheDocument()

      expect(api.patchOffer).toHaveBeenCalledTimes(0)
      expect(api.getOffer).toHaveBeenCalledTimes(0)
      expect(
        screen.queryByText('There is the summary route content')
      ).not.toBeInTheDocument()

      expect(
        await screen.findByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).toBeInTheDocument()

      const cancelSendMailButton = await screen.findByText('Ne pas envoyer')
      await userEvent.click(cancelSendMailButton)

      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()

      expect(api.patchOffer).toHaveBeenCalledTimes(1)
      expect(api.patchOffer).toHaveBeenCalledWith(offer.id, expectedBody)
      expect(api.getOffer).toHaveBeenCalledTimes(1)
      expect(
        await screen.findByText('There is the summary route content')
      ).toBeInTheDocument()
    })

    it('should not submit when user click on close withdrawal dialog button', async () => {
      const individualStock = individualStockFactory()
      contextOverride.offer = {
        ...offer,
        venueId: virtualVenueId,
        subcategoryId: 'SCID virtual',
        isEvent: false,
        stocks: [individualStock],
      }
      props = {
        venueId: virtualVenueId.toString(),
        offererId: offererId.toString(),
      }

      renderInformationsScreen(props, contextOverride, features)

      const nameField = screen.getByLabelText('Titre de l’offre')
      await userEvent.clear(nameField)
      await userEvent.type(nameField, 'Le nom de mon offre édité')

      const withdrawalDetailsField = await screen.getByDisplayValue(
        'Offer withdrawalDetails'
      )
      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )

      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })

      const submitButton = await screen.findByText(
        'Enregistrer les modifications'
      )

      await userEvent.click(submitButton)

      expect(
        await screen.findByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).toBeInTheDocument()

      const closewithdrawalDialogButton = await screen.getByRole('button', {
        name: 'Fermer la modale',
      })
      await userEvent.click(closewithdrawalDialogButton)

      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()

      expect(api.patchOffer).toHaveBeenCalledTimes(0)
      expect(api.getOffer).toHaveBeenCalledTimes(0)
      expect(screen.getByText('Titre de l’offre')).toBeInTheDocument()
    })

    /**
     * In Order:
     *  - No change on widthdrawal and bookingsQuantity
     *  - change but no bookingsQuantity
     *  - No change and no bookingsQuantity
     */
    const shouldNotOpenConditions = [
      {
        modifyWithdrawailDetails: false,
        hasBookingQuantity: true,
      },
      {
        modifyWithdrawailDetails: true,
        hasBookingQuantity: false,
      },
      {
        modifyWithdrawailDetails: false,
        hasBookingQuantity: false,
      },
    ]
    it.each(shouldNotOpenConditions)(
      "should not open widthdrawal send mail modal when user doesn't change withdrawal and stocks has bookingQuantity and submit form",
      async condition => {
        const individualStock = individualStockFactory()
        if (!condition.hasBookingQuantity) {
          individualStock.bookingsQuantity = 0
        }
        contextOverride.offer = {
          ...offer,
          venueId: virtualVenueId,
          subcategoryId: 'SCID virtual',
          isEvent: true,
          withdrawalDelay: undefined,
          withdrawalType: null,
          stocks: [individualStock],
        }
        props = {
          venueId: virtualVenueId.toString(),
          offererId: offererId.toString(),
        }
        renderInformationsScreen(props, contextOverride, features)

        const nameField = screen.getByLabelText('Titre de l’offre')
        await userEvent.clear(nameField)
        await userEvent.type(nameField, 'Le nom de mon offre édité')

        if (condition.modifyWithdrawailDetails) {
          const withdrawalDetailsField = await screen.getByDisplayValue(
            'Offer withdrawalDetails'
          )
          await userEvent.click(withdrawalDetailsField)
          await userEvent.clear(withdrawalDetailsField)
          await userEvent.type(
            withdrawalDetailsField,
            'Nouvelle information de retrait'
          )
          expectedBody.withdrawalDetails = 'Nouvelle information de retrait'
          await waitFor(() => {
            expect(screen.getByText('Nouvelle information de retrait'))
          })
        }

        const submitButton = await screen.findByText(
          'Enregistrer les modifications'
        )

        await userEvent.click(submitButton)

        expect(
          screen.queryByText(
            'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
          )
        ).not.toBeInTheDocument()

        expect(api.patchOffer).toHaveBeenCalledTimes(1)
        expect(api.patchOffer).toHaveBeenCalledWith(offer.id, expectedBody)
        await waitFor(() => {
          expect(api.getOffer).toHaveBeenCalledTimes(1)
        })
        expect(
          await screen.findByText('There is the summary route content')
        ).toBeInTheDocument()
      }
    )

    it('should not open widthdrawal dialog if offer is not active', async () => {
      const individualStock = individualStockFactory()
      contextOverride.offer = {
        ...offer,
        venueId: virtualVenueId,
        subcategoryId: 'SCID virtual',
        isEvent: true,
        withdrawalDelay: undefined,
        withdrawalType: WithdrawalTypeEnum.NO_TICKET,
        stocks: [individualStock],
        isActive: false,
      }

      props = {
        venueId: virtualVenueId.toString(),
        offererId: offererId.toString(),
      }
      renderInformationsScreen(props, contextOverride, features)
      expectedBody.withdrawalDelay = null
      expectedBody.withdrawalType = WithdrawalTypeEnum.NO_TICKET

      const nameField = screen.getByLabelText('Titre de l’offre')
      await userEvent.clear(nameField)
      await userEvent.type(nameField, 'Le nom de mon offre édité')

      const withdrawalDetailsField = await screen.getByDisplayValue(
        'Offer withdrawalDetails'
      )
      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )
      expectedBody.withdrawalDetails = 'Nouvelle information de retrait'
      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })

      const submitButton = await screen.findByText(
        'Enregistrer les modifications'
      )
      await userEvent.click(submitButton)

      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()

      await waitFor(() => {
        expect(api.patchOffer).toHaveBeenCalledTimes(1)
      })
      expect(api.patchOffer).toHaveBeenCalledWith(offer.id, expectedBody)
      expect(
        await screen.findByText('There is the summary route content')
      ).toBeInTheDocument()
    })

    const withdrawalChanges = [
      {
        withdrawalDetails: true,
        withdrawalDelay: false,
        withdrawalType: false,
      },
      {
        withdrawalDetails: false,
        withdrawalDelay: true,
        withdrawalType: false,
      },
      {
        withdrawalDetails: false,
        withdrawalDelay: false,
        withdrawalType: true,
      },
    ]
    it.each(withdrawalChanges)(
      'should open widthdrawal send mail modal when user change withdrawal information and submit',
      async withdrawalInformations => {
        const individualStock = individualStockFactory()
        contextOverride.offer = {
          ...offer,
          venueId: virtualVenueId,
          subcategoryId: 'SCID virtual',
          isEvent: false,
          withdrawalType: WithdrawalTypeEnum.ON_SITE,
          withdrawalDelay: 0,
          stocks: [individualStock],
        }
        if (contextOverride.subCategories) {
          contextOverride.subCategories[0].conditionalFields = [
            'withdrawalDelay',
            'withdrawalType',
          ]
        }

        expectedBody.withdrawalDelay = 0
        expectedBody.withdrawalType = WithdrawalTypeEnum.ON_SITE
        expectedBody.shouldSendMail = true

        props = {
          venueId: virtualVenueId.toString(),
          offererId: offererId.toString(),
        }
        renderInformationsScreen(props, contextOverride, features)

        const nameField = screen.getByLabelText('Titre de l’offre')
        await userEvent.clear(nameField)
        await userEvent.type(nameField, 'Le nom de mon offre édité')

        if (withdrawalInformations.withdrawalDetails) {
          const withdrawalDetailsField = await screen.getByDisplayValue(
            'Offer withdrawalDetails'
          )
          await userEvent.click(withdrawalDetailsField)
          await userEvent.clear(withdrawalDetailsField)
          await userEvent.type(
            withdrawalDetailsField,
            'Nouvelle information de retrait'
          )
          expectedBody.withdrawalDetails = 'Nouvelle information de retrait'
          await waitFor(() => {
            expect(screen.getByText('Nouvelle information de retrait'))
          })
        }

        if (withdrawalInformations.withdrawalDelay) {
          const withdrawalDelayField = await screen.findByLabelText(
            'Heure de retrait'
          )
          await userEvent.selectOptions(withdrawalDelayField, '1 heure')
          expectedBody.withdrawalDelay = 3600
        }

        if (withdrawalInformations.withdrawalType) {
          const withdrawalTypeField = await screen.findByLabelText(
            'Les billets seront envoyés par email'
          )
          await userEvent.click(withdrawalTypeField)
          expectedBody.withdrawalType = WithdrawalTypeEnum.BY_EMAIL
          expectedBody.withdrawalDelay = 60 * 60 * 24
        }

        const submitButton = await screen.findByText(
          'Enregistrer les modifications'
        )

        await userEvent.click(submitButton)

        expect(
          await screen.findByText(
            'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
          )
        ).toBeInTheDocument()

        expect(api.patchOffer).toHaveBeenCalledTimes(0)
        expect(api.getOffer).toHaveBeenCalledTimes(0)
        expect(
          screen.queryByText('There is the summary route content')
        ).not.toBeInTheDocument()

        const sendMailButton = await screen.findByText('Envoyer un email')
        await userEvent.click(sendMailButton)

        expect(
          screen.queryByText(
            'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
          )
        ).not.toBeInTheDocument()

        expect(api.patchOffer).toHaveBeenCalledTimes(1)
        expect(api.patchOffer).toHaveBeenCalledWith(offer.id, expectedBody)
        expect(api.getOffer).toHaveBeenCalledTimes(1)
        expect(
          await screen.findByText('There is the summary route content')
        ).toBeInTheDocument()
      }
    )
  })
})
