import {
  collectiveFormatEventDate,
  expectOffersOrBookingsAreFound,
  logInAndGoToPage,
} from '../support/helpers.ts'
  
  describe('Adage confirmation', () => {
    let login: string
    let offer: { id: number, name: string, venueName: string }
    let stock: { startDatetime: string}
    let providerApiKey: string
  
    beforeEach(() => {
      cy.visit('/connexion')
      cy.request({
        method: 'GET',
        url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_active_collective_offer',
      }).then((response) => {
        login = response.body.user.email
        offer = response.body.offer
        stock = response.body.stock
        providerApiKey = response.body.providerApiKey
      })
      cy.intercept({ method: 'GET', url: '/collective/offers?offererId=1' }).as(
        'collectiveOffers'
      )
      cy.intercept({
        method: 'GET',
        url: '/collective/offers?offererId=1&status=BOOKED',
      }).as('collectiveOffersBOOKED')
      cy.intercept({
        method: 'GET',
        url: '/collective/offers?offererId=1&status=PREBOOKED',
      }).as('collectiveOffersPREBOOKED')
      cy.intercept({ method: 'GET', url: '/collective/offers/1' }).as(
        'collectiveOfferDetails'
      )
    })
  
    it('I should be able to search with several filters and see expected results', () => {
      logInAndGoToPage(login, '/offres/collectives')
      cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

      cy.stepLog({ message: 'I click on the offer' })

      cy.findAllByTestId('offer-item-row').find('a').contains(offer.name).click()

      cy.wait('@collectiveOfferDetails')
      cy.stepLog({ message: 'I check that the offer is published' })
      cy.contains("Récapitulatif")
      cy.contains('publiée')

      cy.visit('/offres/collectives')

      cy.stepLog({ message: 'Mock the Adage pré-confirmation from the teacher' })
      cy.request({
        method: 'POST',
        url: `http://localhost:5001/v2/collective/adage_mock/offer/${offer.id}/book`,
        headers: {
          'Authorization': `Bearer ${providerApiKey}`,
          'Content-Type': 'application/json',
        },
        body: {}
      }).then((response) => {
        const { bookingId } = response.body

        cy.stepLog({ message: `The offer is now prebooked with a booking id ${bookingId}` })

        cy.stepLog({ message: 'I search with status "PREBOOKED"' })
        cy.get('#search-status').click()
        cy.get('#list-status').find('#option-display-PREBOOKED').click()

        // We click outside the filter to close it
        cy.findByRole('heading', { name: 'Offres collectives' }).click()

        cy.stepLog({ message: 'I validate my filters' })
        cy.findByText('Rechercher').click()
        cy.wait('@collectiveOffersPREBOOKED')
          .its('response.statusCode')
          .should('eq', 200)

        let expectedResults = [
          ['', '', '', 'Titre', 'Date de l’évènement', 'Lieu', 'Établissement', 'Statut'],
          [
            '',
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

        cy.stepLog({ message: 'Mock the Adage confirmation from the headmaster' })
        cy.request({
          method: 'POST',
          url: `http://localhost:5001/v2/collective/adage_mock/bookings/${bookingId}/confirm`,
          headers: {
            'Authorization': `Bearer ${providerApiKey}`,
            'Content-Type': 'application/json',
          },
          body: {}
        })

        cy.stepLog({ message: 'The offer is now confirmed' })

        cy.stepLog({ message: 'I reset all filters' })
        cy.findByText('Réinitialiser les filtres').click()

        cy.stepLog({ message: 'Status filter is empty' })
        cy.findByTestId('wrapper-search-status').within(() => {
          cy.get('select').invoke('val').should('be.empty')
        })

        cy.stepLog({ message: 'I search with status "BOOKED"' })
        cy.get('#search-status').click()
        cy.get('#list-status').find('#option-display-BOOKED').click()

        // We click outside the filter to close it
        cy.findByRole('heading', { name: 'Offres collectives' }).click()

        cy.stepLog({ message: 'I validate my filters' })

        cy.findByText('Rechercher').click()
        cy.wait('@collectiveOffersBOOKED')
          .its('response.statusCode')
          .should('eq', 200)

        expectedResults = [
          ['', 'Titre',  'Date de l’évènement', 'Lieu', 'Établissement', 'Statut'],
          [
            '',
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
      })
    })
  })
