import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  PatchOfferBodyModel,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import {
  GetIndividualOfferFactory,
  offerVenueFactory,
} from 'utils/apiFactories'
import {
  individualOfferCategoryFactory,
  individualOfferContextFactory,
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import InformationsScreen, {
  InformationsScreenProps,
} from '../InformationsScreen'

vi.mock('screens/IndividualOffer/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

const renderInformationsScreen = (
  props: InformationsScreenProps,
  contextOverride: IndividualOfferContextValues
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }
  const contextValue = individualOfferContextFactory(contextOverride)

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <InformationsScreen {...props} />
            </IndividualOfferContext.Provider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })}
          element={<div>There is the summary route content</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
      ],
    }
  )
}

const scrollIntoViewMock = vi.fn()

describe('screens:IndividualOffer::Informations:edition', () => {
  let props: InformationsScreenProps
  let contextOverride: IndividualOfferContextValues
  let offer: GetIndividualOfferResponseModel
  let subCategories: SubcategoryResponseModel[]
  const offererId = 1
  const physicalVenueId = 1
  const virtualVenueId = 2
  const offerId = 12

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const categories = [individualOfferCategoryFactory({ id: 'CID' })]
    subCategories = [
      individualOfferSubCategoryFactory({
        id: SubcategoryIdEnum.ABO_JEU_VIDEO,
        categoryId: 'CID',
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      individualOfferSubCategoryFactory({
        id: SubcategoryIdEnum.CONCERT,
        categoryId: 'CID',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    const venue1: IndividualOfferVenueItem = individualOfferVenueItemFactory()
    const venue2: IndividualOfferVenueItem = individualOfferVenueItemFactory({
      isVirtual: true,
    })

    offer = GetIndividualOfferFactory({
      id: offerId,
      extraData: {
        author: 'Offer author',
        gtl_id: '07000000',
        performer: 'Offer performer',
        ean: '',
        showSubType: '',
        showType: '',
        stageDirector: 'Offer stageDirector',
        speaker: 'Offer speaker',
        visa: '',
      },
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isActive: true,
      isDuo: false,
      isEvent: true,
      isDigital: false,
      isNational: false,
      name: 'Offer name',
      subcategoryId: SubcategoryIdEnum.CONCERT,
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      lastProvider: null,
      status: OfferStatus.ACTIVE,
    })

    contextOverride = individualOfferContextFactory({
      offerId: offer.id,
      offer: offer,
      venueList: [venue1, venue2],
      offererNames: [{ id: offererId, name: 'Offerer name' }],
      categories,
      subCategories,
    })

    props = {
      venueId: physicalVenueId.toString(),
      offererId: offererId.toString(),
    }

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
  })

  it('should submit minimal physical offer and redirect to summary', async () => {
    renderInformationsScreen(props, contextOverride)
    const nameField = screen.getByLabelText('Titre de l’offre *')
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
        gtl_id: '07000000',
        performer: 'Offer performer',
        ean: '',
        musicType: '',
        musicSubType: '',
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
    expect(
      await screen.findByText('There is the summary route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should submit minimal virtual offer and redirect to summary', async () => {
    contextOverride.offer = {
      ...offer,
      venue: offerVenueFactory({ id: virtualVenueId }),
      subcategoryId: SubcategoryIdEnum.ABO_JEU_VIDEO,
      isEvent: false,
      withdrawalDelay: undefined,
      withdrawalType: null,
    }
    props = {
      venueId: virtualVenueId.toString(),
      offererId: offererId.toString(),
    }

    renderInformationsScreen(props, contextOverride)
    const nameField = screen.getByLabelText('Titre de l’offre *')
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
        gtl_id: '07000000',
        performer: 'Offer performer',
        ean: '',
        musicType: '',
        musicSubType: '',
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
    expect(
      await screen.findByText('There is the summary route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(api.postOffer).not.toHaveBeenCalled()
  })

  it('should delete offer image', async () => {
    contextOverride.offer = {
      ...offer,
      activeMediation: {
        thumbUrl: 'https://image.url',
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
      activeMediation: {
        thumbUrl: 'https://image.url',
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

  it('should go back to summary when clicking on "Annuler et quitter"', async () => {
    renderInformationsScreen(props, contextOverride)

    await userEvent.click(screen.getByText('Annuler et quitter'))

    expect(
      screen.getByText('There is the summary route content')
    ).toBeInTheDocument()
  })

  describe('send mail on withdrawal changes', () => {
    let expectedBody: PatchOfferBodyModel

    beforeEach(() => {
      expectedBody = {
        audioDisabilityCompliant: true,
        bookingEmail: 'booking@email.com',
        description: 'Offer description',
        durationMinutes: 140,
        externalTicketOfficeUrl: 'https://external.example.com',
        extraData: {
          author: 'Offer author',
          gtl_id: '07000000',
          performer: 'Offer performer',
          ean: '',
          musicType: '',
          musicSubType: '',
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
      contextOverride.offer = {
        ...offer,
        venue: offerVenueFactory({ id: virtualVenueId }),
        subcategoryId: SubcategoryIdEnum.ABO_JEU_VIDEO,
        isEvent: false,
        bookingsCount: 1,
      }
      props = {
        venueId: virtualVenueId.toString(),
        offererId: offererId.toString(),
      }
      expectedBody.withdrawalDelay = 140
      expectedBody.withdrawalType = WithdrawalTypeEnum.ON_SITE

      renderInformationsScreen(props, contextOverride)

      const nameField = screen.getByLabelText('Titre de l’offre *')
      await userEvent.clear(nameField)
      await userEvent.type(nameField, 'Le nom de mon offre édité')

      const withdrawalDetailsField = screen.getByDisplayValue(
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

      const cancelSendMailButton = await screen.findByText('Ne pas envoyer')
      await userEvent.click(cancelSendMailButton)

      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()

      expect(api.patchOffer).toHaveBeenCalledTimes(1)
      expect(api.patchOffer).toHaveBeenCalledWith(offer.id, expectedBody)
      expect(
        await screen.findByText('There is the summary route content')
      ).toBeInTheDocument()
    })

    it('should not submit when user click on close withdrawal dialog button', async () => {
      contextOverride.offer = {
        ...offer,
        venue: offerVenueFactory({ id: virtualVenueId }),
        subcategoryId: SubcategoryIdEnum.ABO_JEU_VIDEO,
        isEvent: false,
        bookingsCount: 1,
      }
      props = {
        venueId: virtualVenueId.toString(),
        offererId: offererId.toString(),
      }

      renderInformationsScreen(props, contextOverride)

      const nameField = screen.getByLabelText('Titre de l’offre *')
      await userEvent.clear(nameField)
      await userEvent.type(nameField, 'Le nom de mon offre édité')

      const withdrawalDetailsField = screen.getByDisplayValue(
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

      const closewithdrawalDialogButton = screen.getByRole('button', {
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
      expect(screen.getByText('Titre de l’offre *')).toBeInTheDocument()
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
      async (condition) => {
        contextOverride.offer = {
          ...offer,
          venue: offerVenueFactory({ id: virtualVenueId }),
          subcategoryId: SubcategoryIdEnum.ABO_JEU_VIDEO,
          isEvent: true,
          withdrawalDelay: undefined,
          withdrawalType: null,
          bookingsCount: condition.hasBookingQuantity ? 1 : 0,
        }
        props = {
          venueId: virtualVenueId.toString(),
          offererId: offererId.toString(),
        }
        renderInformationsScreen(props, contextOverride)

        const nameField = screen.getByLabelText('Titre de l’offre *')
        await userEvent.clear(nameField)
        await userEvent.type(nameField, 'Le nom de mon offre édité')

        if (condition.modifyWithdrawailDetails) {
          const withdrawalDetailsField = screen.getByDisplayValue(
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
        expect(
          await screen.findByText('There is the summary route content')
        ).toBeInTheDocument()
      }
    )

    it('should not open widthdrawal dialog if offer is not active', async () => {
      contextOverride.offer = {
        ...offer,
        venue: offerVenueFactory({ id: virtualVenueId }),
        subcategoryId: SubcategoryIdEnum.ABO_JEU_VIDEO,
        isEvent: true,
        withdrawalDelay: undefined,
        withdrawalType: WithdrawalTypeEnum.NO_TICKET,
        isActive: false,
      }

      props = {
        venueId: virtualVenueId.toString(),
        offererId: offererId.toString(),
      }
      renderInformationsScreen(props, contextOverride)
      expectedBody.withdrawalDelay = null
      expectedBody.withdrawalType = WithdrawalTypeEnum.NO_TICKET

      const nameField = screen.getByLabelText('Titre de l’offre *')
      await userEvent.clear(nameField)
      await userEvent.type(nameField, 'Le nom de mon offre édité')

      const withdrawalDetailsField = screen.getByDisplayValue(
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
      async (withdrawalInformations) => {
        contextOverride.offer = {
          ...offer,
          venue: offerVenueFactory({ id: virtualVenueId }),
          subcategoryId: SubcategoryIdEnum.ABO_JEU_VIDEO,
          isEvent: false,
          withdrawalType: WithdrawalTypeEnum.ON_SITE,
          withdrawalDelay: 0,
          bookingsCount: 1,
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
        renderInformationsScreen(props, contextOverride)

        const nameField = screen.getByLabelText('Titre de l’offre *')
        await userEvent.clear(nameField)
        await userEvent.type(nameField, 'Le nom de mon offre édité')

        if (withdrawalInformations.withdrawalDetails) {
          const withdrawalDetailsField = screen.getByDisplayValue(
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
          const withdrawalDelayField =
            await screen.findByLabelText('Heure de retrait *')
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
        expect(
          await screen.findByText('There is the summary route content')
        ).toBeInTheDocument()
      }
    )
  })
})
