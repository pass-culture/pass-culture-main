import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('The cookie banner should be displayed', () => {
  cy.contains('Respect de votre vie privée').should('be.visible')
})

Then('The cookie banner should not be displayed', () => {
  cy.contains('Respect de votre vie privée').should('not.exist')
})

When('I decline all cookies', () => {
  cy.findByText('Tout refuser').click()
})

When('I accept all cookies', () => {
  cy.findByText('Tout accepter').click()
})

When('I open the cookie management option', () => {
  cy.findByText('Gestion des cookies').click()
})

Then('I should have {int} items checked', (int: number) => {
  cy.get(".orejime-AppItem input[type='checkbox']:checked").should(
    'have.length',
    int
  )
})

When('I open the choose cookies option', () => {
  cy.findByText('Choisir les cookies').click()
})

When('I select the {string} cookie', (s: string) => {
  cy.findByText(s).click()
})

When('I save my choices', () => {
  cy.findByText('Enregistrer mes choix').click()
})

Then('The Beamer cookie should be checked', () => {
  cy.get('#orejime-app-item-beamer').should('be.checked')
})

Then('The Beamer cookie should not be checked', () => {
  cy.get('#orejime-app-item-beamer').should('not.be.checked')
})

When('I close the cookie option', () => {
  cy.get('.orejime-Modal-closeButton').click()
})

When('I clear all cookies in Browser', () => {
  cy.clearCookies()
})
