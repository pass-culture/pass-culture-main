describe('Modify a digital individual offer', () => {
  const login = 'activation@example.com'
  const password = 'user@AZERTY123'

  before(() => {
    cy.visit('/connexion')
    cy.setFeatureFlags([{ name: 'WIP_SPLIT_OFFER', isActive: true }])
    // cy.request({
    //   method: 'GET',
    //   url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    // }).then((response) => {
    //   login = response.body.user.email
    // })
  })

  it('I should be able to modify the url of a digital offer', function () {
    // I am logged in with account 2
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    // I go to the "Offres" page
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })

    // I open the first offer in the list
    cy.findAllByTestId('offer-item-row')
      .first()
      .within(() => {
        cy.findByRole('link', { name: 'Modifier' }).click()
      })
    cy.url().should('contain', '/recapitulatif')

    // I display Informations pratiques tab
    cy.findByText('Informations pratiques').click()
    cy.url().should('contain', '/pratiques')

    // I edit the offer displayed
    cy.get('a[aria-label^="Modifier les détails de l’offre"]').click()
    cy.url().should('contain', '/edition/pratiques')

    // I update the url link
    const randomUrl = `http://myrandomurl${Math.random().toString().substring(2, 5)}.fr/`
    cy.get('input#url').clear().type(randomUrl)
    cy.findByText('Enregistrer les modifications').click()
    cy.findAllByTestId('global-notification-success').should(
      'contain',
      'Vos modifications ont bien été enregistrées'
    )
    cy.findByText('Retour à la liste des offres').click()
    cy.url().should('contain', '/offres')
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
    cy.contains('Offres individuelles')

    // I open the first offer in the list
    cy.findAllByTestId('offer-item-row')
      .first()
      .within(() => {
        cy.findByRole('link', { name: 'Modifier' }).click()
      })
    cy.url().should('contain', '/recapitulatif')

    // I display Informations pratiques tab
    cy.findByText('Informations pratiques').click()
    cy.url().should('contain', '/pratiques')

    // the url updated is retrieved in the details of the offer
    cy.contains('URL d’accès à l’offre : ' + randomUrl)
  })
})
