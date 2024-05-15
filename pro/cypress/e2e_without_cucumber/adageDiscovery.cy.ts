describe('Adage discovery', () => {
  beforeEach(() => {
    cy.visit('/connexion')
    cy.getFakeAdageToken()

    cy.intercept({
      method: 'GET',
      url: 'adage-iframe/playlists/new_template_offers',
    }).as('getNewTemplateOffersPlaylist')
  })

  it('should redirect to adage discovery', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.url().should('include', '/decouverte')
    cy.findByRole('link', { name: 'Découvrir' }).should(
      'have.attr',
      'aria-current',
      'page'
    )
    cy.contains('Découvrez la part collective du pass Culture')
  })

  it('should redirect to adage search page with filtered venue', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}&venue=1`)
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher' }).should(
      'have.attr',
      'aria-current',
      'page'
    )
    cy.findByRole('button', { name: /Lieu : Librairie des GTls/ })
  })

  it('should redirect to a page dedicated to the offer with an active header on the discovery tab', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.findAllByTestId('card-offer-link').first().click()

    cy.findAllByRole('link', { name: 'Découvrir' }).should(
      'have.attr',
      'aria-current',
      'page'
    )
  })

  it('should redirect to search page with filtered domain on click in domain card', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.findAllByTestId('card-domain-link').first().click()

    cy.findByRole('link', { name: 'Rechercher' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.findByRole('button', { name: /Architecture/ })
  })

  it('should redirect to search page with filtered venue on click in venue card', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.findAllByTestId('card-venue-link').first().scrollIntoView()

    cy.findAllByTestId('card-venue-link').first().within(($cardVenuelink) => {
      cy.findByTestId('venue-infos-name').then($btn => {
        const buttonLabel = $btn.text()
        cy.wrap(buttonLabel).as('buttonLabel')
      })
    })
    cy.findAllByTestId('card-venue-link').first().click()

    cy.findByRole('link', { name: 'Rechercher' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.get('@buttonLabel').then(buttonLabel => {
      cy.get(`button[title="Supprimer Lieu :  ${buttonLabel}"]`).click()
    })
  })

  it('should not keep filters after page change', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.findAllByTestId('card-venue-link').first().scrollIntoView()
    cy.findAllByTestId('card-venue-link').first().within(($cardVenuelink) => {
      cy.findByTestId('venue-infos-name').then($btn => {
        const buttonLabel = $btn.text()
        cy.wrap(buttonLabel).as('buttonLabel')
      })
  })
    cy.findAllByTestId('card-venue-link').first().click()

    cy.findByRole('link', { name: 'Rechercher' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.get('@buttonLabel').then(buttonLabel => {
      cy.get(`button[title="Supprimer Lieu :  ${buttonLabel}"]`)
    })

    cy.findByRole('link', { name: 'Découvrir' }).click()

    cy.findByRole('link', { name: 'Rechercher' }).click()

    cy.get('title').contains("Supprimer Lieu").should('not.exist')
})

  it('should put an offer in favorite', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.wait('@getNewTemplateOffersPlaylist')

    cy.findAllByTestId('card-offer')
      .first()
      .invoke('text')
      .then((text: string) => {
        cy.findAllByTestId('favorite-inactive').first().click()
        cy.contains('Ajouté à vos favoris')

        cy.contains('Mes Favoris').click()

        cy.contains(text)

        cy.findByRole('link', { name: 'Découvrir' }).click()

        cy.reload()

        cy.findAllByTestId('favorite-active').first().click()
      })
  })
})
