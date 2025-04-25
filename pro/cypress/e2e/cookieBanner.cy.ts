import { logInAndGoToPage } from '../support/helpers.ts'

describe('Cookie management with no login', () => {
  beforeEach(() => {
    cy.visit('/connexion')
  })

  it('The cookie banner should remain displayed when opening a new page', () => {
    cy.wrap(Cypress.session.clearAllSavedSessions())
    cy.stepLog({ message: 'I clear all cookies in Browser' })
    cy.clearCookies()

    cy.stepLog({
      message: 'I click on the "Accessibilité : non conforme" link',
    })
    cy.findByText('Accessibilité : non conforme').click()

    cy.stepLog({ message: 'the cookie banner should be displayed' })
    cy.contains('Respect de votre vie privée').should('be.visible')
  })

  it('I should be able to accept all cookies, and all the cookies are checked in the dialog', () => {
    cy.stepLog({ message: 'the cookie banner should be displayed' })
    cy.contains('Respect de votre vie privée').should('be.visible')

    cy.stepLog({ message: 'I accept all cookies' })
    cy.findByText('Tout accepter').click()

    cy.stepLog({ message: 'the cookie banner should not be displayed' })
    cy.contains('Respect de votre vie privée').should('not.exist')

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'I should have 4 items checked' })
    cy.get('.orejime-Purpose-children .orejime-Purpose-input:checked').should(
      'have.length',
      4
    )

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({
      message: 'I click on the "Accessibilité : non conforme" link',
    })
    cy.findByText('Accessibilité : non conforme').click()

    cy.stepLog({ message: 'the cookie banner should not be displayed' })
    cy.contains('Respect de votre vie privée').should('not.exist')
  })

  it('I should be able to refuse all cookies, and no cookie is checked in the dialog, except the required', () => {
    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.findAllByText('Tout accepter').last().click()
    cy.stepLog({ message: 'I decline all cookies' })
    cy.findAllByText('Tout refuser').last().click()

    cy.stepLog({ message: 'I should have 1 item checked' })
    cy.get('.orejime-Purpose-children .orejime-Purpose-input:checked').should(
      'have.length',
      1
    )
  })

  it('I should be able to choose a specific cookie, save and the status should be the same on modal re display', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'I check the option status' })
    cy.get('#orejime-purpose-beamer').should('not.be.checked')

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'the Beamer cookie should be checked' })
    cy.get('#orejime-purpose-beamer').should('be.checked')
  })

  it('I should be able to choose a specific cookie, reload the page and the status should not have been changed', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'I check the option status' })
    cy.get('#orejime-purpose-beamer').should('not.be.checked')

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I open the "connexion" page' })
    cy.visit('/connexion')

    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'the Beamer cookie should not be checked' })
    cy.get('#orejime-purpose-beamer').should('not.be.checked')
  })

  it('I should be able to choose a specific cookie, close the modal and the status should not have been changed', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I close the cookie option' })
    cy.get('.orejime-Modal-closeButton').click()

    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'the Beamer cookie should be checked' })
    cy.get('#orejime-purpose-beamer').should('not.be.checked')
  })

  it('I should be able to choose a specific cookie, clear my cookies, and check that specific cookie not checked', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({ message: 'I clear all cookies and storage' })
    cy.clearAllCookies()
    cy.clearAllLocalStorage()
    cy.clearAllSessionStorage()

    cy.visit('/connexion')

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'the Beamer cookie should not be checked' })
    cy.get('#orejime-purpose-beamer').should('not.be.checked')
  })
})

describe('Cookie management with login', () => {
  it('I should be able to choose a specific cookie, log in with another account and check that specific cookie is checked', () => {
    cy.stepLog({ message: 'I clear all cookies in Browser' })
    cy.clearCookies()

    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user_already_onboarded',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/accueil', false)
      }
    )

    cy.stepLog({ message: 'I close the collective budget information modal' })
    cy.findAllByText('Fermer').click()

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({ message: 'I disconnect of my account' })
    cy.findByTestId('offerer-select').click()
    cy.findByTestId('header-dropdown-menu-div').should('exist')
    cy.contains('Se déconnecter').click()
    cy.url().should('contain', '/connexion')

    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user_already_onboarded',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/accueil', false)
      }
    )

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findAllByText('Gestion des cookies').first().click()

    cy.stepLog({ message: 'the Beamer cookie should be checked' })
    cy.get('#orejime-purpose-beamer').should('be.checked')
  })
})
