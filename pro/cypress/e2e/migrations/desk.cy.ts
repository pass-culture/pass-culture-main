describe('Desk (Guichet) feature', () => {
  const login = 'activation@example.com'
  const password = 'user@AZERTY123'

  before(() => {
    // cy.request({
    //   method: 'GET',
    //   url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    // }).then((response) => {
    //   login = response.body.user.email
    // })
  })

  beforeEach(() => {
    cy.visit('/connexion')
    cy.stepLog({ message: 'I am logged in with account' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })

    cy.stepLog({ message: 'I go to the "Guichet" page' })
    cy.url().then((urlSource) => {
      cy.findAllByText('Guichet').first().click()
      cy.url().should('not.equal', urlSource)
    })
  })

  it('I should see the top of the page when changing page', () => {
    cy.stepLog({ message: 'The identity check message is displayed' })
    cy.findByText(
      'N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque.'
    )
    cy.findByText(
      'Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.'
    )

    cy.stepLog({
      message: 'I can click and open the "Modalités de retrait et CGU" page',
    })
    cy.findByText('Modalités de retrait et CGU')
      .invoke('removeAttr', 'target')
      .click() // remove target to not open it in a new tab (not supported by cypress)
    cy.origin('https://aide.passculture.app/', () => {
      cy.url().should(
        'include',
        'Acteurs-Culturels-Modalit%C3%A9s-de-retrait-et-CGU'
      )
    })
  })

  it("Saisie et validation d'une nouvelle contremarque @todo: besoin de données, absentes dans la sandbox", () => {
    cy.stepLog({ message: 'I add this countermark "2XTM3W"' })
    cy.findByLabelText('Contremarque').type('2XTM3W')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: 'the booking is done' })
    // @todo: Write code here that turns the phrase above into concrete actions
  })

  it('It should decline a non-valid countermark', () => {
    cy.stepLog({ message: 'I add this countermark "XXXXXX"' })
    cy.findByLabelText('Contremarque').type('XXXXXX')

    cy.stepLog({ message: 'the countermark is rejected as invalid' })
    cy.findByTestId('desk-message').should(
      'have.text',
      "La contremarque n'existe pas"
    )
    cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it("Saisie et invalidation d'une contremarque déjà validée @todo: besoin de données, absentes dans la sandbox", () => {
    cy.stepLog({ message: 'I add this countermark "2XTM3W"' })
    cy.findByLabelText('Contremarque').type('2XTM3W')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: 'Contremarque déjà validée' })
    // @todo: check que se passe-t-il ???
    // cy.findByTestId('desk-message').should(
    //   'have.text',
    //   "La contremarque n'existe pas"
    // )
    // cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it("Saisie d'une contremarque d'un autre pro @todo: besoin de données, absentes dans la sandbox", () => {
    //  @todo: besoin de données, absentes dans la sandbox", () => {
    cy.stepLog({ message: 'I add this countermark "??????"' })
    cy.findByLabelText('Contremarque').type('??????')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: "contremarque d'un autre pro" })
    // @todo: check que se passe-t-il ???
    // cy.findByTestId('desk-message').should(
    //   'have.text',
    //   "La contremarque n'existe pas"
    // )
    // cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it("Saisie de la contremarque d'une réservation non confirmée @todo: besoin de données, absentes dans la sandbox", () => {
    cy.stepLog({ message: 'I add this countermark "??????"' })
    cy.findByLabelText('Contremarque').type('??????')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: "contremarque d'une réservation non confirmée" })
    // @todo: check que se passe-t-il ???
    // cy.findByTestId('desk-message').should(
    //   'have.text',
    //   "La contremarque n'existe pas"
    // )
    // cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it("Saisie de la contremarque d'une réservation annulée @todo: besoin de données, absentes dans la sandbox", () => {
    cy.stepLog({ message: 'I add this countermark "??????"' })
    cy.findByLabelText('Contremarque').type('??????')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: "contremarque d'une réservation annulée" })
    // @todo: check que se passe-t-il ???
    // cy.findByTestId('desk-message').should(
    //   'have.text',
    //   "La contremarque n'existe pas"
    // )
    // cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it("Saisie de la contremarque d'une réservation déjà remboursée @todo: besoin de données, absentes dans la sandbox", () => {
    cy.stepLog({ message: 'I add this countermark "??????"' })
    cy.findByLabelText('Contremarque').type('??????')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: "contremarque d'une réservation déjà remboursée" })
    // @todo: check que se passe-t-il ???
    // cy.findByTestId('desk-message').should(
    //   'have.text',
    //   "La contremarque n'existe pas"
    // )
    // cy.findByText('Valider la contremarque').should('be.disabled')
  })
})
