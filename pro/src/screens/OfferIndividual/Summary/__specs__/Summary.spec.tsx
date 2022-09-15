import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { configureTestStore } from 'store/testUtils'

import Summary, { ISummaryProps } from '../Summary'

const mockLogEvent = jest.fn()

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

describe('Summary', () => {
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
      isVirtual: true,
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
      url: 'https://offer-url.example.com',
      venueName: venue.name,
      venuePublicName: venue.publicName,
      isVenueVirtual: venue.isVirtual,
      offererName: 'mon offerer',
      bookingEmail: 'booking@example.com',
      externalTicketOfficeUrl: 'https://grand-public-url.example.com',
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
    it('should render component with informations', async () => {
      // given / when
      renderSummary(props)

      // then
      expect(await screen.getAllByText('Modifier')).toHaveLength(2)
      expect(await screen.getByText("Détails de l'offre")).toBeInTheDocument()
      expect(await screen.getByText("Type d'offre")).toBeInTheDocument()
      expect(
        await screen.getByText('Informations artistiques')
      ).toBeInTheDocument()
      expect(
        await screen.getByText('Informations pratiques')
      ).toBeInTheDocument()
      expect(await screen.getByText('Accessibilité')).toBeInTheDocument()
      expect(
        await screen.getByText('Notifications des réservations')
      ).toBeInTheDocument()
      expect(await screen.getByText('Stocks et prix')).toBeInTheDocument()
      expect(
        await screen.getByText('URL d’accès à l’offre', { exact: false })
      ).toBeInTheDocument()
      expect(
        await screen.getByText('Lien pour le grand public')
      ).toBeInTheDocument()
      expect(await screen.getByText("Aperçu dans l'app")).toBeInTheDocument()

      expect(
        await screen.getByText(props.offer.categoryName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.subCategoryName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.offererName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.venuePublicName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.withdrawalDetails)
      ).toBeInTheDocument()
      expect(await screen.getByText(props.offer.url)).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.externalTicketOfficeUrl)
      ).toBeInTheDocument()
      expect(await screen.getByText('Non accessible')).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.bookingEmail)
      ).toBeInTheDocument()
      expect(await screen.getByText('0 €')).toBeInTheDocument()
      expect(await screen.getByText('Illimité')).toBeInTheDocument()
      expect(await screen.getAllByText(props.offer.name)).toHaveLength(2)
      expect(await screen.getAllByText(props.offer.description)).toHaveLength(2)
      expect(
        await screen.getByText('Retour à la liste des offres')
      ).toBeInTheDocument()
      expect(
        await screen.getByText('Visualiser dans l’app')
      ).toBeInTheDocument()
    })
  })

  describe('On Creation', () => {
    beforeEach(() => {
      props.isCreation = true
    })

    it('should render component with informations', async () => {
      // given / when
      renderSummary(props)

      // then
      expect(await screen.getAllByText('Modifier')).toHaveLength(2)
      expect(await screen.getByText("Détails de l'offre")).toBeInTheDocument()
      expect(await screen.getByText("Type d'offre")).toBeInTheDocument()
      expect(
        await screen.getByText('Informations artistiques')
      ).toBeInTheDocument()
      expect(
        await screen.getByText('Informations pratiques')
      ).toBeInTheDocument()
      expect(await screen.getByText('Accessibilité')).toBeInTheDocument()
      expect(
        await screen.getByText('Notifications des réservations')
      ).toBeInTheDocument()
      expect(await screen.getByText('Stocks et prix')).toBeInTheDocument()
      expect(
        await screen.getByText('URL d’accès à l’offre', { exact: false })
      ).toBeInTheDocument()
      expect(
        await screen.getByText('Lien pour le grand public')
      ).toBeInTheDocument()

      expect(await screen.getByText("Aperçu dans l'app")).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.categoryName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.subCategoryName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.offererName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.venuePublicName)
      ).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.withdrawalDetails)
      ).toBeInTheDocument()
      expect(await screen.getByText(props.offer.url)).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.externalTicketOfficeUrl)
      ).toBeInTheDocument()
      expect(await screen.getByText('Non accessible')).toBeInTheDocument()
      expect(
        await screen.getByText(props.offer.bookingEmail)
      ).toBeInTheDocument()
      expect(await screen.getByText('0 €')).toBeInTheDocument()
      expect(await screen.getByText('Illimité')).toBeInTheDocument()
      expect(await screen.getAllByText(props.offer.name)).toHaveLength(2)
      expect(await screen.getAllByText(props.offer.description)).toHaveLength(2)
      expect(
        await screen.queryByText('Visualiser dans l’app')
      ).not.toBeInTheDocument()
    })

    describe('When it is form v2', () => {
      it('should render component with right buttons', async () => {
        // given / when
        renderSummary(props)

        // then
        expect(await screen.getByText('Étape précédente')).toBeInTheDocument()
        expect(await screen.getByText("Publier l'offre")).toBeInTheDocument()
      })
    })

    describe('When it is form v3', () => {
      it('should render component with right buttons', async () => {
        // given
        props.formOfferV2 = false

        // when
        renderSummary(props)

        // then
        expect(await screen.getByText('Précédent')).toBeInTheDocument()
        expect(await screen.getByText('Suivant')).toBeInTheDocument()
        expect(await screen.getByText('Annuler')).toBeInTheDocument()
      })
    })
  })
})
