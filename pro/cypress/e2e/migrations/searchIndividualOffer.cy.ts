import { addDays, format } from 'date-fns'

describe('Search individual offers', () => {
  const login = 'retention_structures@example.com'
  const password = 'user@AZERTY123'

  beforeEach(() => {
    cy.visit('/connexion')
    // cy.request({
    //   method: 'GET',
    //   url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user_with_offers', // @todo
    // }).then((response) => {
    //   login = response.body.user.email
    // })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })
  })

  it('A search with a name should display expected results', () => {
    // I select offerer "Cinéma du coin" in offer page
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getOffererId'
    )
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Cinéma du coin')
      .click()
    cy.wait('@getOffererId')
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    // I search with the text "Mon offre brouillon avec stock"
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
      'Mon offre brouillon avec stock'
    )

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // These results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      [
        '',
        '',
        'Mon offre brouillon avec stock',
        'Espace des Gnoux',
        '1 000',
        'brouillon',
      ],
    ]
    const reLAbelCount = new RegExp(1 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < 1; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('have.text', bookLineArray[column])
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })

  it('A search with a EAN should display expected results', () => {
    // I select offerer "Réseau de librairies" in offer page
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getOffererId'
    )
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Réseau de librairies')
      .click()
    cy.wait('@getOffererId')
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    // I search with the text "9780000000004"
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
      '9780000000004'
    )

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // These 10 results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 9',
        '10',
        'désactivée',
      ],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 8', '10', 'publiée'],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 7', '10', 'publiée'],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 6',
        '10',
        'en attente',
      ],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 5', '10', 'publiée'],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 4', '10', 'publiée'],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 3',
        '10',
        'désactivée',
      ],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 2', '10', 'publiée'],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 1', '10', 'publiée'],
    ]
    const reLAbelCount = new RegExp(10 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 10)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < 10; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('have.text', bookLineArray[column])
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })

  it('A search with "Catégories" filter should display expected results', () => {
    // I select "Instrument de musique" in "Catégories"
    cy.findByLabelText('Catégories').select('Instrument de musique')

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // These results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', 'Offer', 'Terrain vague', '20', 'publiée'], // @Romain: Offer et pas Offer 1679 car id change en sandbox
    ]
    const reLAbelCount = new RegExp(1 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < 1; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('contain.text', bookLineArray[column]) // @romain: et donc ici pas de vérification stricte, mais avec Factory oui
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })

  it('A search by offer status should display expected results', () => {
    // I select offerer "Réseau de librairies" in offer page
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getOffererId'
    )
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Réseau de librairies')
      .click()
    cy.wait('@getOffererId')
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    // I select "Publiée" in offer status
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').select('Publiée')
    })

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // These 28 results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 3 avec EAN9780000000003',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 2 avec EAN9780000000002',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 1 avec EAN9780000000001',
        'Librairie 10',
        '10',
        'publiée',
      ],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 8', '10', 'publiée'],
      ['', '', 'Livre 3 avec EAN9780000000003', 'Librairie 8', '10', 'publiée'],
      ['', '', 'Livre 2 avec EAN9780000000002', 'Librairie 8', '10', 'publiée'],
      ['', '', 'Livre 1 avec EAN9780000000001', 'Librairie 8', '10', 'publiée'],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 7', '10', 'publiée'],
      ['', '', 'Livre 3 avec EAN9780000000003', 'Librairie 7', '10', 'publiée'],
    ]
    const reLAbelCount = new RegExp(28 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 10)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < 10; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('have.text', bookLineArray[column])
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })

  it('A search by date should display expected results', () => {
    // I select offerer "Michel Léon" in offer page
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getOffererId'
    )
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu').findByText('Michel Léon').click()
    cy.wait('@getOffererId')
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    // I select a date in one month
    const dateSearch = format(addDays(new Date(), 30), 'yyyy-MM-dd')
    cy.findByLabelText('Début de la période').type(dateSearch)
    cy.findByLabelText('Fin de la période').type(dateSearch)

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // These results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      [
        '',
        '',
        "Un concert d'electro inoubliable",
        'Michel',
        '1 000',
        'publiée',
      ],
    ]
    const reLAbelCount = new RegExp(1 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < 1; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('contain.text', bookLineArray[column]) // @romain: et donc ici pas de vérification stricte, mais avec Factory oui
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })

  it('A search combining several filters should display expected results', () => {
    // I select offerer "Réseau de librairies" in offer page
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getOffererId'
    )
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Réseau de librairies')
      .click()
    cy.wait('@getOffererId')
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    // I search with the text "Livre"
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
      'Livre'
    )

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // I select "Livre" in "Catégories"
    cy.findByLabelText('Catégories').select('Livre')

    // I select "Librairie 10" in "Lieu"
    cy.findByLabelText('Lieu').select('Librairie 10')

    // I select "Publiée" in offer status
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').select('Publiée')
    })

    // I validate my filters
    cy.intercept({
      method: 'GET',
      url: '/offers?*',
      times: 1,
    }).as('searchOffers')
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers')

    // These 4 results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', 'Livre 4 avec EAN', 'Librairie 10', '10', 'publiée'],
      ['', '', 'Livre 3 avec EAN', 'Librairie 10', '10', 'publiée'],
      ['', '', 'Livre 2 avec EAN', 'Librairie 10', '10', 'publiée'],
      ['', '', 'Livre 1 avec EAN', 'Librairie 10', '10', 'publiée'],
    ]
    const reLAbelCount = new RegExp(4 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 4)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < 4; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('contain.text', bookLineArray[column]) // @romain: et donc ici pas de vérification stricte, mais avec Factory oui
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }

    // I reset all filters
    cy.findByText('Réinitialiser les filtres').click()

    // All filters are empty
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').should(
      'be.empty'
    )
    cy.findByTestId('wrapper-lieu').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-categorie').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-creationMode').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByLabelText('Début de la période').invoke('val').should('be.empty')
    cy.findByLabelText('Fin de la période').invoke('val').should('be.empty')

    // These 40 results should be displayed
    const data2 = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 3 avec EAN9780000000003',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 2 avec EAN9780000000002',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 1 avec EAN9780000000001',
        'Librairie 10',
        '10',
        'publiée',
      ],
      [
        '',
        '',
        'Livre 4 avec EAN9780000000004',
        'Librairie 9',
        '10',
        'désactivée',
      ],
      [
        '',
        '',
        'Livre 3 avec EAN9780000000003',
        'Librairie 9',
        '10',
        'désactivée',
      ],
      [
        '',
        '',
        'Livre 2 avec EAN9780000000002',
        'Librairie 9',
        '10',
        'désactivée',
      ],
      [
        '',
        '',
        'Livre 1 avec EAN9780000000001',
        'Librairie 9',
        '10',
        'désactivée',
      ],
      ['', '', 'Livre 4 avec EAN9780000000004', 'Librairie 8', '10', 'publiée'],
      ['', '', 'Livre 3 avec EAN9780000000003', 'Librairie 8', '10', 'publiée'],
    ]
    const reLAbelCount2 = new RegExp(40 + ' ' + '(offre|réservation)', 'g')

    cy.findAllByTestId('offer-item-row').should('have.length', 10)
    cy.contains(reLAbelCount2)

    for (let rowLine = 0; rowLine < 10; rowLine++) {
      const bookLineArray = data2[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('have.text', bookLineArray[column]) // @romain: et donc ici pas de vérification stricte, mais avec Factory oui
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })
})
