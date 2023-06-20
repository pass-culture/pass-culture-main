import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useOfferWizardMode from 'hooks/useOfferWizardMode'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { api } from '../../../../apiClient/api'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from '../../../../context/OfferIndividualContext'
import Summary from '../Summary'

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
  customContext: Partial<IOfferIndividualContext> = {},
  customOverrides?: any
) => {
  const context = {
    ...defaultContext,
    ...customContext,
  }
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    ...customOverrides,
  }

  return renderWithProviders(
    <OfferIndividualContext.Provider value={context}>
      <Summary />
    </OfferIndividualContext.Provider>,
    { storeOverrides }
  )
}

describe('Summary trackers', () => {
  let customContext: Partial<IOfferIndividualContext>
  const offerId = 15

  beforeEach(() => {
    customContext = {
      offer: individualOfferFactory({ nonHumanizedId: offerId }),
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
      renderSummary(customContext)

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
          offerId: offerId,
          used: 'RecapLink',
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(customContext)

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
          to: 'tarifs',
          used: 'RecapLink',
          isDraft: false,
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on return to offers button', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on see preview link', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })
  })

  describe('On Creation', () => {
    beforeEach(() => {
      customContext.offer = individualOfferFactory({
        nonHumanizedId: offerId,
        status: OfferStatus.DRAFT,
      })
      jest
        .spyOn(useOfferWizardMode, 'default')
        .mockImplementation(() => OFFER_WIZARD_MODE.CREATION)
    })

    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(customContext)

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
          to: 'tarifs',
          used: 'RecapLink',
          isDraft: true,
          offerId: offerId,
        }
      )
    })

    describe('When it is form v2', () => {
      it('should track when clicking on return to previous step button', async () => {
        // given
        renderSummary(customContext)

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
            offerId: offerId,
          }
        )
      })

      it('should track when clicking on return to publish offer button', async () => {
        // given
        renderSummary(customContext)

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
            offerId: offerId,
          }
        )
      })
    })

    it('should track when clicking on return to previous step button', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
          isDraft: true,
        }
      )
    })

    it('should track when clicking on publish button', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })
  })

  describe('For Draft offers', () => {
    beforeEach(() => {
      customContext.offer = individualOfferFactory({
        nonHumanizedId: offerId,
        status: OfferStatus.DRAFT,
      })
      jest
        .spyOn(useOfferWizardMode, 'default')
        .mockImplementation(() => OFFER_WIZARD_MODE.DRAFT)
    })

    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(customContext)

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
          to: 'tarifs',
          used: 'RecapLink',
          isDraft: true,
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on return to previous step button', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on return to publish offer button', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on return to save draft button', async () => {
      // given
      renderSummary(customContext)

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
          offerId: offerId,
        }
      )
    })
  })

  describe('First offer Pop in', () => {
    const venueId = 1
    beforeEach(async () => {
      jest
        .spyOn(useOfferWizardMode, 'default')
        .mockImplementation(() => OFFER_WIZARD_MODE.CREATION)

      jest.spyOn(api, 'patchPublishOffer').mockResolvedValue()

      const context = {
        ...defaultContext,
        offer: individualOfferFactory({
          nonHumanizedId: offerId,
          status: OfferStatus.DRAFT,
        }),
        venueId: venueId,
        showVenuePopin: {
          [venueId]: true,
        },
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

      renderSummary(context, overrideStore)

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
          venue_id: venueId,
        }
      )
    })
  })
})
