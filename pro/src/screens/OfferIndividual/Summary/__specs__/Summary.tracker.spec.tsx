import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useOfferWizardMode from 'hooks/useOfferWizardMode'
import { renderWithProviders } from 'utils/renderWithProviders'

import { api } from '../../../../apiClient/api'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from '../../../../context/OfferIndividualContext'
import * as useNewOfferCreationJourney from '../../../../hooks/useNewOfferCreationJourney'
import Summary, { ISummaryProps } from '../Summary'

const mockLogEvent = jest.fn()
window.open = jest.fn()

jest.mock('apiClient/api', () => ({
  api: { patchPublishOffer: jest.fn().mockResolvedValue({}) },
}))

const defaultContext: IOfferIndividualContext = {
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
}

const renderSummary = (
  props: ISummaryProps,
  context: IOfferIndividualContext = defaultContext,
  customOverrides?: any
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    ...customOverrides,
  }

  return renderWithProviders(
    <OfferIndividualContext.Provider value={context}>
      <Summary {...props} />
    </OfferIndividualContext.Provider>,
    { storeOverrides }
  )
}

describe('Summary trackers', () => {
  let props: ISummaryProps

  beforeEach(() => {
    const categories = [
      {
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      },
    ]
    const subCategories = [
      {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'A-B',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    const venue = {
      name: 'ma venue',
      publicName: 'ma venue (nom public)',
      isVirtual: false,
    }

    const stock = {
      quantity: null,
      price: 0,
      bookingLimitDatetime: null,
    }

    const offer = {
      id: 'AB',
      nonHumanizedId: 1,
      name: 'mon offre',
      description: 'ma description',
      categoryName: categories[0].proLabel,
      subCategoryName: subCategories[0].proLabel,
      subcategoryId: subCategories[0].id,
      accessibility: {
        visual: false,
        audio: false,
        motor: false,
        mental: false,
        none: true,
      },
      isDuo: false,
      author: 'jean-mich',
      stageDirector: 'jean-mich',
      speaker: 'jean-mich',
      visa: '0123',
      performer: 'jean-mich',
      isbn: '0123',
      durationMinutes: '01:00',
      url: '',
      externalTicketOfficeUrl: '',
      venueName: venue.name,
      venuePublicName: venue.publicName,
      isVenueVirtual: venue.isVirtual,
      offererName: 'mon offerer',
      bookingEmail: 'booking@example.com',
      withdrawalDetails: 'détails de retrait',
      withdrawalType: null,
      withdrawalDelay: null,
      status: OfferStatus.ACTIVE,
    }
    const preview = {
      offerData: {
        name: offer.name,
        description: offer.description,
        isEvent: false,
        isDuo: offer.isDuo,
      },
    }

    props = {
      offerId: offer.id,
      nonHumanizedOfferId: offer.nonHumanizedId,
      providerName: null,
      offer: offer,
      stockThing: stock,
      stockEventList: undefined,
      subCategories: subCategories,
      preview: preview,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest
      .spyOn(useOfferWizardMode, 'default')
      .mockImplementation(() => OFFER_WIZARD_MODE.EDITION)
  })

  describe('On edition', () => {
    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(screen.getAllByText('Modifier')[0])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'informations',
          isDraft: false,
          offerId: 'AB',
          used: 'RecapLink',
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(screen.getAllByText('Modifier')[1])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'stocks',
          used: 'RecapLink',
          isDraft: false,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on return to offers button', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(
        await screen.findByText('Retour à la liste des offres')
      )

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'Offers',
          used: 'StickyButtons',
          isDraft: false,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on see preview link', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.findByText('Visualiser dans l’app'))

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'AppPreview',
          used: 'SummaryPreview',
          isDraft: false,
          offerId: 'AB',
        }
      )
    })
  })

  describe('On Creation', () => {
    beforeEach(() => {
      props.offer.status = OfferStatus.DRAFT
      jest
        .spyOn(useOfferWizardMode, 'default')
        .mockImplementation(() => OFFER_WIZARD_MODE.CREATION)
    })

    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(screen.getAllByText('Modifier')[0])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          to: 'informations',
          used: 'RecapLink',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(screen.getAllByText('Modifier')[1])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          to: 'stocks',
          used: 'RecapLink',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })

    describe('When it is form v2', () => {
      it('should track when clicking on return to previous step button', async () => {
        // given
        renderSummary(props)

        // when
        await userEvent.click(await screen.findByText('Étape précédente'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'recapitulatif',
            isEdition: false,
            to: 'stocks',
            used: 'StickyButtons',
            isDraft: true,
            offerId: 'AB',
          }
        )
      })

      it('should track when clicking on return to publish offer button', async () => {
        // given
        renderSummary(props)

        // when
        await userEvent.click(await screen.findByText('Publier l’offre'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'recapitulatif',
            isEdition: false,
            to: 'confirmation',
            used: 'StickyButtons',
            isDraft: true,
            offerId: 'AB',
          }
        )
      })
    })

    it('should track when clicking on return to previous step button', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.findByText('Étape précédente'))

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          to: 'stocks',
          used: 'StickyButtons',
          offerId: 'AB',
          isDraft: true,
        }
      )
    })

    it('should track when clicking on publish button', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.findByText('Publier l’offre'))

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          to: 'confirmation',
          used: 'StickyButtons',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })
  })

  describe('For Draft offers', () => {
    beforeEach(() => {
      props.offer.status = OfferStatus.DRAFT
      jest
        .spyOn(useOfferWizardMode, 'default')
        .mockImplementation(() => OFFER_WIZARD_MODE.DRAFT)
    })

    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(screen.getAllByText('Modifier')[0])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'informations',
          used: 'RecapLink',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(screen.getAllByText('Modifier')[1])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'stocks',
          used: 'RecapLink',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on return to previous step button', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.findByText('Étape précédente'))

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'stocks',
          used: 'StickyButtons',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on return to publish offer button', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.findByText('Publier l’offre'))

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'confirmation',
          used: 'StickyButtons',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })

    it('should track when clicking on return to save draft button', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(
        await screen.findByText('Sauvegarder le brouillon et quitter')
      )

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'Offers',
          used: 'DraftButtons',
          isDraft: true,
          offerId: 'AB',
        }
      )
    })
  })

  describe('First offer Pop in', () => {
    beforeEach(async () => {
      props.offer.status = OfferStatus.DRAFT
      jest
        .spyOn(useOfferWizardMode, 'default')
        .mockImplementation(() => OFFER_WIZARD_MODE.CREATION)

      jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)
      jest.spyOn(api, 'patchPublishOffer').mockResolvedValue()

      const context = defaultContext
      context.venueId = 'AB'
      context.showVenuePopin = {
        AB: true,
      }
      const overrideStore = {
        features: {
          initialized: true,
          list: [
            {
              isActive: true,
              nameKey: 'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
            },
          ],
        },
      }

      renderSummary(props, context, overrideStore)

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )
    })

    it("Should track user click on 'later' button", async () => {
      expect(
        screen.getByText('Félicitations, vous avez créé votre offre !')
      ).toBeInTheDocument()

      await userEvent.click(await screen.findByText('Plus tard'))

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(2)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL,
        {
          from: 'recapitulatif',
        }
      )
    })

    it("Should track user click on 'add pricing point' button", async () => {
      expect(
        screen.getByText('Félicitations, vous avez créé votre offre !')
      ).toBeInTheDocument()
      await userEvent.click(
        await screen.findByText('Renseigner des coordonnées bancaires')
      )

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(2)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON,
        {
          from: 'recapitulatif',
          venue_id: 'AB',
        }
      )
    })
  })
})
