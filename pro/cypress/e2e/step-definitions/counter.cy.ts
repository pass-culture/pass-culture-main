import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

Then('Identity check message is displayed', () => {
  cy.findByTestId('desk-callout-message')
    .should(
      'contain',
      'N’oubliez pas de vérifier l’identité du bénéficiaire avant de\n            valider la contremarque'
    )
    .and(
      'contain',
      'Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.Modalités de retrait et CGU'
    )
})

When('I can click and open {string} page', (link: string) => {
  cy.findByText(link).invoke('removeAttr','target').click() // remove target to not open it in a new tab (not supported by cypress)
  cy.origin('https://aide.passculture.app/', () => {
    cy.url().should('include', 'Acteurs-Culturels-Modalit%C3%A9s-de-retrait-et-CGU')
  })
})

Then('The booking is done', () => {
  // Write code here that turns the phrase above into concrete actions
})

When('I add this countermark {string}', (countermark: string) => {
  cy.findByLabelText('Contremarque').type(countermark)
})

When('I validate the countermark', () => {
    cy.findByText('Valider la contremarque').click()
})

Then('The countermark is refused because invalid', () => {
  cy.findByTestId('desk-message').should('have.text', 'La contremarque n\'existe pas')
  cy.findByText('Valider la contremarque').should('be.disabled')
})


