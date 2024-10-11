describe('Navigation', () => {
  let login = ''
  const password = 'user@AZERTY123'

  before(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    }).then((response) => {
      login = response.body.user.email
    })
  })

  it('I should see the top of the page when changing page', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.findByText('Bienvenue dans l’espace acteurs culturels')
    cy.findByText('Vos adresses')
    cy.findByText('Ajouter un lieu')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I scroll to my venue' })
    cy.findByText('Votre page partenaire').scrollIntoView().should('be.visible')
    cy.findByText('Vos adresses').scrollIntoView().should('be.visible')
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
