import { homePageLoaded, logAndGoToPage } from '../support/helpers.ts'

describe('Cookie management with no login', () => {
  beforeEach(() => {
    cy.visit('/connexion')
  })

  it('The cookie banner should remain displayed when opening a new page', () => {
    cy.stepLog({ message: 'I decline all cookies' })
    cy.findByText('Tout refuser').click()

    cy.stepLog({ message: 'I clear all cookies in Browser' })
    cy.clearCookies()

    cy.stepLog({
      message: 'I click on the "Accessibilité : non conforme" link',
    })
    cy.findByText('Accessibilité : non conforme').click()

    cy.stepLog({ message: 'the cookie banner should be displayed' })
    cy.contains('Respect de votre vie privée').should('be.visible')
  })

  it('The user can accept all, and all the cookies are checked in the dialog', () => {
    cy.stepLog({ message: 'the cookie banner should be displayed' })
    cy.contains('Respect de votre vie privée').should('be.visible')

    cy.stepLog({ message: 'I accept all cookies' })
    cy.findByText('Tout accepter').click()

    cy.stepLog({ message: 'the cookie banner should not be displayed' })
    cy.contains('Respect de votre vie privée').should('not.exist')

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'I should have 4 items checked' })
    cy.get(".orejime-AppItem input[type='checkbox']:checked").should(
      'have.length',
      4
    )
  })

  it('The user can refuse all, and no cookie is checked in the dialog, except the required', () => {
    cy.stepLog({ message: 'I decline all cookies' })
    cy.findByText('Tout refuser').click()

    cy.stepLog({ message: 'the cookie banner should not be displayed' })
    cy.contains('Respect de votre vie privée').should('not.exist')

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'I should have 1 item checked' })
    cy.get(".orejime-AppItem input[type='checkbox']:checked").should(
      'have.length',
      1
    )
  })

  it('The user can choose a specific cookie, save and the status should be the same on modal re display', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findByText('Choisir les cookies').click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'the Beamer cookie should be checked' })
    cy.get('#orejime-app-item-beamer').should('be.checked')
  })

  it('The user can choose a specific cookie, reload the page and the status should not have been changed', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findByText('Choisir les cookies').click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I open the "connexion" page' })
    cy.visit('/connexion')

    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findByText('Choisir les cookies').click()

    cy.stepLog({ message: 'the Beamer cookie should not be checked' })
    cy.get('#orejime-app-item-beamer').should('not.be.checked')
  })

  it('The user can choose a specific cookie, close the modal and the status should not have been changed', () => {
    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findByText('Choisir les cookies').click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I close the cookie option' })
    cy.get('.orejime-Modal-closeButton').click()

    cy.stepLog({ message: 'I open the choose cookies option' })
    cy.findByText('Choisir les cookies').click()

    cy.stepLog({ message: 'the Beamer cookie should be checked' })
    cy.get('#orejime-app-item-beamer').should('be.checked')
  })
})

describe('Cookie management with login', () => {
  const password = 'user@AZERTY123'

  beforeEach(() => {
    cy.visit('/connexion')
  })

  it('The user can choose a specific cookie, log in with another account and check that specific cookie is checked', () => {
    cy.stepLog({ message: 'I clear all cookies in Browser' })
    cy.clearCookies()

    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    }).then((response) => {
      const login = response.body.user.email
      cy.stepLog({ message: 'I am logged in with account 1' })
      cy.log('login: ' + login)
      cy.login({
        email: login,
        password: password,
        redirectUrl: '/',
      })
    })

    homePageLoaded()

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({ message: 'I disconnect of my account' })
    cy.findByTestId('offerer-select').click()
    cy.findByTestId('header-dropdown-menu-div').should('exist')
    cy.contains('Se déconnecter').click()
    cy.url().should('contain', '/connexion')

    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    }).then((response) => {
      const login = response.body.user.email
      cy.stepLog({
        message: 'I am logged in with account 2 and no cookie selection',
      })
      cy.login({
        email: login,
        password: password,
        refusePopupCookies: false,
      })
    })

    homePageLoaded()

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'the Beamer cookie should be checked' })
    cy.get('#orejime-app-item-beamer').should('be.checked')
  })

  it('The user log in, choose a specific cookie, open another browser, log in again and check that specific cookie not checked', () => {
    // Cypress cannot deal with 2 browsers or a tab. So we log out, and log in again with a clean browser
    // See https://docs.cypress.io/guides/references/trade-offs#Multiple-browsers-open-at-the-same-time
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    }).then((response) => {
      cy.wrap(response.body.user.email).as('login')
    })

    cy.stepLog({ message: 'I clear all cookies in Browser' })
    cy.clearCookies()

    cy.stepLog({ message: 'I am logged in with account 3' })
    cy.get('@login').then((login) =>
      logAndGoToPage(login.toString(), '/accueil')
    )

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'I select the "Beamer" cookie' })
    cy.findByText('Beamer').click()

    cy.stepLog({ message: 'I save my choices' })
    cy.findByText('Enregistrer mes choix').click()

    cy.stepLog({ message: 'I disconnect of my account' })
    cy.findByTestId('offerer-select').click()
    cy.findByTestId('header-dropdown-menu-div').should('exist')
    cy.contains('Se déconnecter').click()
    cy.url().should('contain', '/connexion')

    cy.stepLog({ message: 'I clear all cookies and storage' })
    cy.clearAllCookies()
    cy.clearAllLocalStorage()
    cy.clearAllSessionStorage()

    cy.stepLog({ message: 'I am logged in with account 3' })
    cy.get('@login').then((login) =>
      logAndGoToPage(login.toString(), '/accueil')
    )

    cy.stepLog({ message: 'I open the cookie management option' })
    cy.findByText('Gestion des cookies').click()

    cy.stepLog({ message: 'the Beamer cookie should not be checked' })
    cy.get('#orejime-app-item-beamer').should('not.be.checked')
  })
})
