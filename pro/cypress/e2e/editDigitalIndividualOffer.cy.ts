import { addDays, format } from 'date-fns'

import { logInAndGoToPage } from '../support/helpers.ts'

describe('Edit digital individual offers', () => {
  describe('Display and url modification', () => {
    let login1: string
    beforeEach(() => {
      cy.wrap(Cypress.session.clearAllSavedSessions())
      cy.visit('/connexion')
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/pro/create_regular_pro_user_with_virtual_offer',
        (response) => {
          login1 = response.body.user.email
        }
      )
    })

    it('An edited offer is displayed with 4 links', function () {
      logInAndGoToPage(login1, '/offre/individuelle/1/recapitulatif/details')

      cy.contains('Récapitulatif')

      cy.stepLog({ message: 'I check that the 4 links are displayed' })
      cy.findByRole('link', { name: 'Lien actif Détails de l’offre' }).should(
        'exist'
      )
      cy.findByRole('link', { name: 'Informations pratiques' }).should('exist')
      cy.findByRole('link', { name: 'Stock & Prix' }).should('exist')
      cy.findAllByRole('link', { name: 'Réservations' }).eq(1).should('exist')
    })

    it('I should be able to modify the url of a digital offer', function () {
      logInAndGoToPage(login1, '/offres')

      cy.stepLog({ message: 'I open the first offer in the list' })
      cy.findAllByTestId('offer-item-row')
        .first()
        .within(() => {
          cy.findByRole('button', { name: 'Voir les actions' }).click()
        })
      cy.findByRole('menuitem', { name: 'Voir l’offre' }).click()
      cy.url().should('contain', '/recapitulatif')

      cy.findByRole('link', { name: 'Modifier les détails de l’offre' }).click()

      cy.stepLog({ message: 'I update the url link' })
      const randomUrl = `http://myrandomurl.fr/`
      cy.get('input#url').type('{selectall}{del}' + randomUrl)

      cy.stepLog({ message: 'I display Informations pratiques tab' })
      cy.findByText('Enregistrer les modifications').click()

      cy.findByText('http://myrandomurl.fr/').should('exist')

      cy.findByText('Informations pratiques').click()
      cy.url().should('contain', '/pratiques')

      cy.stepLog({ message: 'I edit the offer displayed' })
      cy.findByRole('link', { name: 'Modifier les détails de l’offre' }).click()
      cy.url().should('contain', '/edition/pratiques')

      cy.findByText('Enregistrer les modifications').click()
      cy.findByText('Retour à la liste des offres').click()
      cy.url().should('contain', '/offres')
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
      cy.contains('Offres individuelles')

      cy.stepLog({ message: 'I open the first offer in the list' })
      cy.findAllByTestId('offer-item-row')
        .first()
        .within(() => {
          cy.findByRole('button', { name: 'Voir les actions' }).click()
        })
      cy.findByRole('menuitem', { name: 'Voir l’offre' }).click()
      cy.url().should('contain', '/recapitulatif')

      cy.stepLog({ message: 'I display Informations pratiques tab' })
      cy.findByText('Informations pratiques').click()
      cy.url().should('contain', '/pratiques')
    })
  })

  describe('Modification of date event offer with bookings', () => {
    let login2: string
    beforeEach(() => {
      cy.visit('/connexion')
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/pro/create_pro_user_with_bookings',
        (response) => {
          login2 = response.body.user.email
        }
      )
      cy.intercept({ method: 'PATCH', url: '/stocks/bulk' }).as('patchStock')
    })

    it('I should be able to change offer date and it should change date in bookings', function () {
      const newDate = format(addDays(new Date(), 15), 'yyyy-MM-dd')
      logInAndGoToPage(login2, '/offre/individuelle/2/edition/stocks')

      cy.contains('Modifier l’offre')
      cy.findAllByTestId('spinner').should('not.exist')

      cy.stepLog({ message: 'Save initial date of events' })
      cy.findByTestId('stocks.0.beginningDate').then(($elt) => {
        cy.log('date: ' + $elt.val())
        cy.stepLog({ message: '=> Date of event was: ' + $elt.val() })
        cy.stepLog({
          message:
            '=> Type new date of event: ' + format(newDate, 'yyyy-MM-dd'),
        })
        cy.wrap($elt).type('{selectall}{del}' + format(newDate, 'yyyy-MM-dd'))
        cy.findByLabelText('Quantité restante').click()
      })
      cy.findByTestId('stocks.0.bookingLimitDatetime').then(($elt) => {
        cy.log('date: ' + $elt.val())
        cy.stepLog({ message: '=> Date of booking limit was: ' + $elt.val() })
        cy.stepLog({
          message:
            '=> Type new date of booking limit: ' +
            format(newDate, 'yyyy-MM-dd'),
        })
        cy.wrap($elt).type('{selectall}{del}' + format(newDate, 'yyyy-MM-dd'))
        cy.findByLabelText('Quantité restante').click()
      })

      cy.stepLog({ message: 'Save modifications' })
      cy.findByText('Enregistrer les modifications').click()

      cy.stepLog({ message: 'Confirm modifications' })
      cy.findByText('Confirmer les modifications').click()
      cy.wait('@patchStock')
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
