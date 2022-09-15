import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { Events } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS } from 'core/Offers'
import { configureTestStore } from 'store/testUtils'

import Summary, { ISummaryProps } from '../Summary'

const mockLogEvent = jest.fn()
window.open = jest.fn()

jest.mock('repository/pcapi/pcapi', () => ({
  publishOffer: jest.fn().mockResolvedValue({}),
}))

const renderSummary = (props: ISummaryProps) => {
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  })
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Summary {...props} />
      </MemoryRouter>
    </Provider>
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
      formOfferV2: true,
      isCreation: false,
      providerName: null,
      offerStatus: 'DRAFT',
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
  })

  describe('On edition', () => {
    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.getAllByText('Modifier')[0])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          to: 'details',
          used: 'RecapLink',
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.getAllByText('Modifier')[1])

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
        }
      )
    })
  })

  describe('On Creation', () => {
    beforeEach(() => {
      props.isCreation = true
    })

    it('should track when clicking on "Modifier" on offer section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.getAllByText('Modifier')[0])

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          to: 'details',
          used: 'RecapLink',
        }
      )
    })

    it('should track when clicking on "Modifier" on stock section', async () => {
      // given
      renderSummary(props)

      // when
      await userEvent.click(await screen.getAllByText('Modifier')[1])

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
          }
        )
      })

      it('should track when clicking on return to publish offer button', async () => {
        // given
        renderSummary(props)

        // when
        await userEvent.click(await screen.findByText("Publier l'offre"))

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
          }
        )
      })
    })

    describe('When it is form v3', () => {
      beforeEach(() => {
        props.formOfferV2 = false
      })

      it('should track when clicking on return to previous step button', async () => {
        // given
        renderSummary(props)

        // when
        await userEvent.click(await screen.findByText('Précédent'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'recapitulatif',
            isEdition: false,
            to: 'THIS ONE?',
            used: 'StickyButtons',
          }
        )
      })

      it('should track when clicking on return to next step button', async () => {
        // given
        renderSummary(props)

        // when
        await userEvent.click(await screen.findByText('Suivant'))

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
          }
        )
      })

      it('should track when clicking on return to cancel button', async () => {
        // given
        renderSummary(props)

        // when
        await userEvent.click(await screen.findByText('Annuler'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(0)
      })
    })
  })
})
