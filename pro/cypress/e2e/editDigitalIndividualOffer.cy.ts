import { addDays, format } from 'date-fns'

import { DEFAULT_AXE_CONFIG, DEFAULT_AXE_RULES } from '../support/constants.ts'
import { logInAndGoToPage } from '../support/helpers.ts'

describe('Edit digital individual offers', () => {
  describe('Display and url modification', () => {
    let login1: string
    beforeEach(() => {
      cy.visit('/connexion')
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/pro/create_regular_pro_user_with_virtual_offer',
        (response) => {
          login1 = response.body.user.email
        }
      )
    })

    it('An edited offer should be displayed with 5 navigation links', () => {
      logInAndGoToPage(
        login1,
        '/offre/individuelle/1/recapitulatif/description'
      )

      cy.contains('Récapitulatif')
      cy.injectAxe(DEFAULT_AXE_CONFIG)
      cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

      cy.stepLog({ message: 'I check that the 5 links are displayed' })
      cy.findByRole('link', { name: 'Lien actif Description' }).should('exist')
      cy.findByRole('link', { name: 'Localisation' }).should('exist')
      cy.findByRole('link', { name: 'Image et vidéo' }).should('exist')
      cy.findByRole('link', { name: 'Tarifs' }).should('exist')
      cy.findByRole('link', { name: 'Informations pratiques' }).should('exist')
      cy.findAllByRole('link', { name: 'Réservations' }).eq(1).should('exist')
    })

    it('I should be able to modify the url of a digital offer', () => {
      logInAndGoToPage(login1, '/offres')

      //  OFFER SUMMARY PAGE
      cy.stepLog({ message: 'I open the first offer in the list' })
      cy.get('tbody')
        .findByRole('row')
        .first()
        .within(() => {
          cy.findByRole('button', { name: 'Voir les actions' }).click()
        })
      cy.findByRole('menuitem', { name: 'Voir l’offre' }).click()
      cy.url().should('contain', '/recapitulatif')

      //  DESCRIPTION EDITION
      cy.stepLog({ message: 'I edit the offer description' })
      cy.findByRole('link', {
        name: 'Modifier la description de l’offre',
      }).click()
      cy.findByText('Enregistrer les modifications').click()

      cy.findByRole('heading', { name: 'Description' }).should('exist')

      //  LOCATION EDITION
      cy.findByText('Localisation').click()
      cy.url().should('contain', '/localisation')
      cy.stepLog({ message: 'I edit the offer localisation' })
      cy.findByRole('link', {
        name: 'Modifier la localisation de l’offre',
      }).click()
      cy.url().should('contain', '/edition/localisation')
      const randomUrl = `http://myrandomurl.fr/`
      cy.findByLabelText(/URL d’accès à l’offre/).type(
        `{selectall}{del}${randomUrl}`
      )
      cy.findByText('Enregistrer les modifications').click()

      cy.findByText('http://myrandomurl.fr/').should('exist')

      //  OFFERS LIST
      cy.findByText('Retour à la liste des offres').click()
      cy.url().should('contain', '/offres')
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
      cy.contains('Offres individuelles')

      cy.stepLog({ message: 'I open the first offer in the list' })
      cy.get('tbody')
        .findByRole('row')
        .first()
        .within(() => {
          cy.findByRole('button', { name: 'Voir les actions' }).click()
        })
      cy.findByRole('menuitem', { name: 'Voir l’offre' }).click()
      cy.url().should('contain', '/recapitulatif')

      cy.stepLog({ message: 'I display useful informations tab' })
      cy.findByText('Informations pratiques').click()
      cy.url().should('contain', '/informations_pratiques')
    })
  })

  describe('Modification of an offer with timestamped stocks and bookings', () => {
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

    it('I should be able to change offer date and it should change date in bookings', () => {
      const newDate = format(addDays(new Date(), 15), 'yyyy-MM-dd')
      logInAndGoToPage(login2, '/offre/individuelle/2/edition/horaires')

      cy.contains('Modifier l’offre')
      cy.findAllByTestId('spinner').should('not.exist')

      cy.stepLog({ message: 'Save initial date of events and limit date' })

      cy.findAllByRole('button', { name: 'Modifier la date' }).eq(0).click()

      cy.findAllByLabelText('Date *')
        .eq(0)
        .type(`{selectall}{del}${format(newDate, 'yyyy-MM-dd')}`)

      cy.findAllByLabelText('Date *')
        .eq(1)
        .type(`{selectall}{del}${format(newDate, 'yyyy-MM-dd')}`)

      cy.stepLog({ message: 'Save modifications' })
      cy.findByText('Valider').click()

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
