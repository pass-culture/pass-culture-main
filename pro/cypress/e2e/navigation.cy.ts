import { logInAndGoToPage } from '../support/helpers.ts'

describe('Navigation', () => {
  let login: string

  beforeEach(() => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        login = response.body.user.email
      }
    )
  })

  it('I should see the top of the page when changing page', () => {
    logInAndGoToPage(login, '/accueil')

    cy.stepLog({ message: 'I close the collective budget information modal' })
    cy.findAllByText('Fermer').click()

    cy.stepLog({ message: 'I scroll to my venue' })
    cy.contains(
      'h3',
      /Votre page partenaire|Vos pages partenaire/
    ).scrollIntoView()
    cy.contains('h3', /Votre page partenaire|Vos pages partenaire/).should(
      'be.visible'
    )
    cy.get('[id=content-wrapper]').then((el) => {
      expect(el.get(0).scrollTop).to.be.greaterThan(0)
    })

    cy.stepLog({ message: 'I want to update that venue' })
    cy.get('a[aria-label^="Gérer la page Mon Lieu"]').click()

    cy.stepLog({ message: 'I should be at the top of the page' })
    cy.get('[id=top-page]').should('have.focus', { timeout: 1000 })
    cy.get('[id=content-wrapper]').then((el) => {
      expect(el.get(0).scrollTop).to.eq(0)
    })
  })
})
