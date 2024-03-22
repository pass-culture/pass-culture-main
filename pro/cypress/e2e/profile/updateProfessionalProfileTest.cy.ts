import { CONSTANTS } from '../../support/constants'

describe('update professional profile', () => {
  it('update name of the profile and verify required fields', () => {
    cy.login({
      email: CONSTANTS.emailProAccount,
      password: CONSTANTS.passwordProAccount,
    })
    cy.contains('Modifier').click()

    cy.url().should('include', '/profil')

    cy.contains('Modifier').click()

    cy.get(CONSTANTS.firstNameField).clear()

    cy.contains('Enregistrer').click()

    cy.contains('Veuillez renseigner votre prénom').should('be.visible')

    cy.get(CONSTANTS.firstNameField).type(CONSTANTS.firstName)

    cy.get(CONSTANTS.lastNameField).clear()

    cy.contains('Enregistrer').click()

    cy.contains('Veuillez renseigner votre nom').should('be.visible')

    cy.get(CONSTANTS.lastNameField).type(CONSTANTS.lastName)

    cy.contains('Enregistrer').click()

    cy.contains(CONSTANTS.firstName + ' ' + CONSTANTS.lastName).should(
      'be.visible'
    )
  })
})
