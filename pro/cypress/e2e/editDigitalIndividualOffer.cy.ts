import { addDays, format } from 'date-fns'

import { logAndGoToPage } from '../support/helpers.ts'

describe('Edit digital individual offers', () => {
  let login: string

  describe('Display and url modification', () => {
    beforeEach(() => {
      cy.visit('/connexion')
      cy.request({
        method: 'GET',
        url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user_with_virtual_offer',
      }).then((response) => {
        login = response.body.user.email
      })
    })

    it('An edited offer is displayed with 4 tabs', function () {
      logAndGoToPage(login, '/offre/individuelle/1/recapitulatif/details')

      cy.contains('Récapitulatif')

      cy.stepLog({ message: 'I check that the 4 tab are displayed' })
      cy.findByRole('tablist').within(() => {
        cy.findAllByRole('tab').eq(0).should('have.text', 'Détails de l’offre')
        cy.findAllByRole('tab')
          .eq(1)
          .should('have.text', 'Informations pratiques')
        cy.findAllByRole('tab').eq(2).should('have.text', 'Stock & Prix')
        cy.findAllByRole('tab').eq(3).should('have.text', 'Réservations')
      })
    })

    it('I should be able to modify the url of a digital offer', function () {
      logAndGoToPage(login, '/offres')

      cy.stepLog({ message: 'I open the first offer in the list' })
      cy.findAllByTestId('offer-item-row')
        .first()
        .within(() => {
          cy.findByRole('link', { name: 'Modifier' }).click()
        })
      cy.url().should('contain', '/recapitulatif')

      cy.stepLog({ message: 'I display Informations pratiques tab' })
      cy.findByText('Informations pratiques').click()
      cy.url().should('contain', '/pratiques')

      cy.stepLog({ message: 'I edit the offer displayed' })
      cy.get('a[aria-label^="Modifier les détails de l’offre"]').click()
      cy.url().should('contain', '/edition/pratiques')

      cy.stepLog({ message: 'I update the url link' })
      const randomUrl = `http://myrandomurl.fr/`
      cy.get('input#url').type('{selectall}{del}' + randomUrl)
      cy.findByText('Enregistrer les modifications').click()
      cy.findByText('http://myrandomurl.fr/').should('exist')
      cy.findByText('Retour à la liste des offres').click()
      cy.url().should('contain', '/offres')
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
      cy.contains('Offres individuelles')

      cy.stepLog({ message: 'I open the first offer in the list' })
      cy.findAllByTestId('offer-item-row')
        .first()
        .within(() => {
          cy.findByRole('link', { name: 'Modifier' }).click()
        })
      cy.url().should('contain', '/recapitulatif')

      cy.stepLog({ message: 'I display Informations pratiques tab' })
      cy.findByText('Informations pratiques').click()
      cy.url().should('contain', '/pratiques')

      cy.stepLog({
        message: 'the url updated is retrieved in the details of the offer',
      })
      cy.contains('URL d’accès à l’offre : ' + randomUrl)
    })
  })

  describe('Modification of date event offer with bookings', () => {
    beforeEach(() => {
      cy.visit('/connexion')
      cy.request({
        method: 'GET',
        url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_bookings',
      }).then((response) => {
        login = response.body.user.email
      })
    })

    it('I should be able to change offer date and it should change date in bookings', function () {
      const newDate = format(addDays(new Date(), 15), 'yyyy-MM-dd')
      logAndGoToPage(login, '/offre/individuelle/2/edition/stocks')
      cy.contains('Modifier l’offre')
      cy.findAllByTestId('spinner').should('not.exist')

      cy.stepLog({ message: 'Save initial date of events' })
      cy.findByTestId('wrapper-stocks[0]beginningDate').within(() => {
        cy.get('input').then(($elt) => {
          cy.log('date: ' + $elt.val())
          cy.stepLog({ message: '=> Date of event was: ' + $elt.val() })
          cy.stepLog({
            message:
              '=> Type new date of event: ' + format(newDate, 'yyyy-MM-dd'),
          })
          cy.wrap($elt).type('{selectall}{del}' + format(newDate, 'yyyy-MM-dd'))
        })
      })
      cy.findByTestId('wrapper-stocks[0]bookingLimitDatetime').within(() => {
        cy.get('input').then(($elt) => {
          cy.log('date: ' + $elt.val())
          cy.stepLog({ message: '=> Date of booking limit was: ' + $elt.val() })
          cy.stepLog({
            message:
              '=> Type new date of booking limit: ' +
              format(newDate, 'yyyy-MM-dd'),
          })
          cy.wrap($elt).type('{selectall}{del}' + format(newDate, 'yyyy-MM-dd'))
        })
      })

      cy.stepLog({ message: 'Save modifications' })
      cy.findByText('Enregistrer les modifications').click()

      cy.stepLog({ message: 'Confirm modifications' })
      cy.findByText('Confirmer les modifications').click()
      cy.stepLog({ message: 'Check that booking date has been modified' })
      cy.visit('/offre/individuelle/2/reservations')
      cy.findAllByTestId('spinner').should('not.exist')
      cy.get('[data-label="Nom de l’offre"]').should(
        'contain.text',
        format(newDate, 'dd/MM/yyyy')
      )
    })
  })
})
