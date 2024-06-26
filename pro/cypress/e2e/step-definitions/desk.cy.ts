import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

Then('The identity check message is displayed', () => {
  cy.findByText(
    'N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque.'
  )
  cy.findByText(
    'Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.'
  )
})

When('I can click and open the {string} page', (link: string) => {
  cy.findByText(link).invoke('removeAttr', 'target').click() // remove target to not open it in a new tab (not supported by cypress)
  cy.origin('https://aide.passculture.app/', () => {
    cy.url().should(
      'include',
      'Acteurs-Culturels-Modalit%C3%A9s-de-retrait-et-CGU'
    )
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

Then('The countermark is rejected as invalid', () => {
  cy.findByTestId('desk-message').should(
    'have.text',
    "La contremarque n'existe pas"
  )
  cy.findByText('Valider la contremarque').should('be.disabled')
})
