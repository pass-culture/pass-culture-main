describe('cookies banner', () => {
  it('the cookie banner should be displayed', () => {
    cy.visit('/connexion')
    cy.contains('Respect de votre vie privée').should('be.visible')
  })

  it('the cookie banner should be displayed on cookie deletion', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Tout refuser').click()
    cy.clearCookies()
    cy.visit('/connexion')
    cy.contains('Respect de votre vie privée').should('be.visible')
  })

  it('the user can accept all', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Tout accepter').click()
    cy.contains('Respect de votre vie privée').should('not.exist')
  })

  it('the user can accept all, and all the cookies are checked in the dialog', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Tout accepter').click()
    cy.contains('Respect de votre vie privée').should('not.exist')
    cy.get('button').contains('Gestion des cookies').click()
    cy.get(".orejime-AppItem input[type='checkbox']:checked").should(
      'have.length',
      4
    )
  })

  it('the user can refuse all, and no cookie is checked in the dialog, except the required', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Tout refuser').click()
    cy.contains('Respect de votre vie privée').should('not.exist')
    cy.get('button').contains('Gestion des cookies').click()
    cy.get(".orejime-AppItem input[type='checkbox']:checked").should(
      'have.length',
      1
    )
  })

  it('the user can choose a specific cookie, save and the status should be the same on modal re display', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Choisir les cookies').click()
    cy.contains('Beamer').click()
    cy.contains('Enregistrer mes choix').click()
    cy.get('button').contains('Gestion des cookies').click()
    cy.get('#orejime-app-item-beamer').should('be.checked')
  })

  it('the user can choose a specific cookie, reload the page and the status should not have been changed', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Choisir les cookies').click()
    cy.contains('Beamer').click()
    cy.visit('/connexion')
    cy.get('button').contains('Gestion des cookies').click()
    cy.get('#orejime-app-item-beamer').should('not.be.checked')
  })

  it('the user can choose a specific cookie, close the modal and the status should not have been changed', () => {
    cy.visit('/connexion')
    cy.get('button').contains('Choisir les cookies').click()
    cy.contains('Beamer').click()
    cy.get('.orejime-Modal-closeButton').click()
    cy.get('button').contains('Choisir les cookies').click()
    cy.get('#orejime-app-item-beamer').should('be.checked')
  })
})
