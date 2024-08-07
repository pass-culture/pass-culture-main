import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

Then('I should be at the top of the page', () => {
  cy.get('[id=top-page]').should('have.focus', { timeout: 1000 })
  cy.get('[id=content-wrapper]').then((el) => {
    expect(el.get(0).scrollTop).to.eq(0)
  })
})

When('I scroll to my venue', () => {
  cy.findByText('Votre page partenaire').scrollIntoView().should('be.visible')
  cy.findByText('Vos adresses').scrollIntoView().should('be.visible')
  cy.get('[id=content-wrapper]').then((el) => {
    expect(el.get(0).scrollTop).to.be.greaterThan(0)
  })
})

When('I want to update that venue', () => {
  cy.get('a[aria-label^="Gérer la page Espace des Gnoux"]').eq(0).click()
})
