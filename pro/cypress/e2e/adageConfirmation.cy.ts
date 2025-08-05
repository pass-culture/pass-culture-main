import {
  collectiveFormatEventDate,
  expectOffersOrBookingsAreFound,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Adage confirmation', () => {
  let login: string
  let offer: { id: number; name: string; venueName: string }
  let stock: { startDatetime: string }
  let providerApiKey: string
  const email1 = 'collectiveofferfactory+booking@example.com'
  const email2 = 'collectiveofferfactory+booking@example2.com'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_active_collective_offer',
      (response) => {
        expect(response.status).to.eq(200)
        login = response.body.user.email
        offer = response.body.offer
        stock = response.body.stock
        providerApiKey = response.body.providerApiKey
        cy.intercept({
          method: 'GET',
          url: `/collective/offers?offererId=${offer.id}`,
        }).as('collectiveOffers')
        cy.intercept({
          method: 'GET',
          url: '/collective/offers?offererId=1&status=BOOKED',
        }).as('collectiveOffersBOOKED')
        cy.intercept({
          method: 'GET',
          url: '/collective/offers?offererId=1&status=PREBOOKED',
        }).as('collectiveOffersPREBOOKED')
        cy.intercept({
          method: 'GET',
          url: `/collective/offers/${offer.id}`,
        }).as('collectiveOfferDetails')
        cy.sandboxCall(
          'GET',
          'http://localhost:5001/sandboxes/clear_email_list',
          (res) => {
            expect(res.status).to.eq(200)
          }
        )
      }
    )
  })

  it('I should be able to search with several filters and see expected results', () => {
    logInAndGoToPage(login, '/offres/collectives')
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I click on the offer' })

    cy.findAllByTestId('offer-item-row').find('a').contains(offer.name).click()

    cy.wait('@collectiveOfferDetails')
    cy.stepLog({ message: 'I check that the offer is published' })
    cy.contains('Récapitulatif')
    cy.contains('publiée')

    cy.visit('/offres/collectives')

    cy.stepLog({ message: 'Mock the Adage pre-booked from the teacher' })
    cy.request({
      method: 'POST',
      url: `http://localhost:5001/v2/collective/adage_mock/offer/${offer.id}/book`,
      headers: {
        Authorization: `Bearer ${providerApiKey}`,
        'Content-Type': 'application/json',
      },
      body: {},
    }).then((res) => {
      expect(res.status).to.eq(200)
      const { bookingId } = res.body

      cy.stepLog({
        message: `The offer is now prebooked with a booking ID ${bookingId}`,
      })

      cy.stepLog({ message: 'Check email received with booking ID' })
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/get_unique_email',
        (response) => {
          expect(response.status).to.eq(200)
          expect(response.body.To).to.eq(email1 + ', ' + email2)
          expect(response.body.params.BOOKING_ID).to.eq(bookingId)
        }
      )

      cy.stepLog({ message: 'I open the filters' })
      cy.findByText('Filtrer').click()

      cy.stepLog({ message: 'I search with status "PREBOOKED"' })
      cy.findByRole('button', { name: 'Statut' }).click()
      cy.findByText('Préréservée').click()

      // We click outside the filter to close it
      cy.findByLabelText('Statut').click()

      cy.stepLog({ message: 'I validate my filters' })
      cy.findByText('Rechercher').click({ force: true })
      cy.wait('@collectiveOffersPREBOOKED')
        .its('response.statusCode')
        .should('eq', 200)

      let expectedResults = [
        [
          '',
          '',
          'Titre',
          'Date de l’évènement',
          'Lieu',
          'Établissement',
          'Statut',
        ],
        [
          '',
          '',
          offer.name,
          collectiveFormatEventDate(stock.startDatetime),
          offer.venueName,
          'DE LA TOUR',
          'préréservée',
        ],
      ]

      expectOffersOrBookingsAreFound(expectedResults)

      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/clear_email_list',
        (response) => {
          expect(response.status).to.eq(200)
        }
      )

      cy.stepLog({ message: 'Mock the Adage confirmation from the headmaster' })
      cy.request({
        method: 'POST',
        url: `http://localhost:5001/v2/collective/adage_mock/bookings/${bookingId}/confirm`,
        headers: {
          Authorization: `Bearer ${providerApiKey}`,
          'Content-Type': 'application/json',
        },
        body: {},
      }).then((response) => {
        expect(response.status).to.eq(204)
      })

      cy.stepLog({ message: 'The offer is now confirmed' })

      cy.stepLog({
        message: 'Check email received with a To, a Bcc and booking ID',
      })
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/get_unique_email',
        (response) => {
          expect(response.status).to.eq(200)
          expect(response.body.To).to.eq(email1)
          expect(response.body.Bcc).to.eq(email2)
          expect(response.body.params.BOOKING_ID).to.eq(bookingId)
        }
      )

      cy.stepLog({ message: 'I reset all filters' })
      cy.findByText('Réinitialiser les filtres').click()

      cy.stepLog({ message: 'Status filter is empty' })
      cy.findByRole('button', { name: 'Statut' })
        .invoke('val')
        .should('be.empty')

      cy.stepLog({ message: 'I search with status "BOOKED"' })
      cy.findByRole('button', { name: 'Statut' }).click()
      cy.findByText('Réservée').click()

      // We click outside the filter to close it
      cy.findByLabelText('Statut').click()

      cy.stepLog({ message: 'I validate my filters' })

      cy.findByText('Rechercher').click({ force: true })
      cy.wait('@collectiveOffersBOOKED')
        .its('response.statusCode')
        .should('eq', 200)

      expectedResults = [
        [
          '',
          '',
          'Titre',
          'Date de l’évènement',
          'Lieu',
          'Établissement',
          'Statut',
        ],
        [
          '',
          '',
          offer.name,
          collectiveFormatEventDate(stock.startDatetime),
          offer.venueName,
          'DE LA TOUR',
          'réservée',
        ],
      ]

      expectOffersOrBookingsAreFound(expectedResults)

      cy.stepLog({ message: 'I reset all filters' })
      cy.findByText('Réinitialiser les filtres').click()

      cy.stepLog({ message: 'Status filter is empty' })
      cy.findByRole('button', { name: 'Statut' })
        .invoke('val')
        .should('be.empty')

      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/clear_email_list',
        (response) => {
          expect(response.status).to.eq(200)
        }
      )

      cy.stepLog({ message: 'I cancel the booking' })
      cy.findByRole('button', { name: 'Voir les actions' }).click()
      cy.findByText('Annuler la réservation').click()
      cy.findByTestId('confirm-dialog-button-confirm').click()

      cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

      cy.findAllByTestId('global-notification-success').should(
        'contain',
        'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
      )

      cy.stepLog({ message: 'Check email received with a To and Bcc' })
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/get_unique_email',
        (response) => {
          expect(response.status).to.eq(200)
          expect(response.body.To).to.eq(email1)
          expect(response.body.Bcc).to.eq(email2)
        }
      )

      cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)
      cy.stepLog({ message: 'Offer is now canceled' })
      cy.contains('annulée')
      expectedResults = [
        [
          '',
          '',
          'Titre',
          "Date de l'événement",
          'Lieu',
          'Établissement',
          'Statut',
        ],
        [
          '',
          '',
          offer.name,
          collectiveFormatEventDate(stock.startDatetime),
          offer.venueName,
          'DE LA TOUR',
          'annulée',
        ],
      ]
      expectOffersOrBookingsAreFound(expectedResults)
    })
  })
})
