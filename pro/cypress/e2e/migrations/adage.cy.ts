describe('ADAGE discovery', () => {
  let offerId: number
  const offerName = 'Mon offre collective'

  beforeEach(() => {
    // I go to adage login page with valid token
    cy.visit('/connexion')
    cy.getFakeAdageToken()
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_adage_environnement',
    }).then((response) => {
      offerId = response.body.offerId
    })
    cy.intercept(
      'GET',
      'http://localhost:5001/collective/educational-domains'
    ).as('getDomains')
    cy.intercept(
      'POST',
      'https://testinghxxtdue7h0-dsn.algolia.net/**',
      (req) =>
        req.reply({
          statusCode: 200,
          body: {
            results: [
              {
                hits: [
                  {
                    offer: {
                      dateCreated: 1726907257.840899,
                      name: 'offer 280 pour eac_pending_bank_informations template request',
                      students: ['Lycée - Seconde'],
                      subcategoryId: 'EVENEMENT_CINE',
                      domains: [10],
                      educationalInstitutionUAICode: 'all',
                      interventionArea: ['2A', '2B'],
                      schoolInterventionArea: null,
                      eventAddressType: 'other',
                      beginningDatetime: 1726907257.840899,
                      description:
                        'a passionate description of collectiveoffer 98',
                    },
                    offerer: {
                      name: 'eac_pending_bank_informations',
                    },
                    venue: {
                      academy: 'Paris',
                      departmentCode: '75',
                      id: 881,
                      name: 'reimbursementPoint eac_pending_bank_informations',
                      publicName:
                        'reimbursementPoint eac_pending_bank_informations',
                      adageId: '789456',
                    },
                    _geoloc: {
                      lat: 48.87004,
                      lng: 2.3785,
                    },
                    isTemplate: true,
                    formats: ['Projection audiovisuelle'],
                    objectID: `T-${offerId}`,
                    _highlightResult: {
                      offer: {
                        name: {
                          value:
                            'offer 280 pour eac_pending_bank_informations template request',
                          matchLevel: 'none',
                          matchedWords: [],
                        },
                        educationalInstitutionUAICode: {
                          value: 'all',
                          matchLevel: 'none',
                          matchedWords: [],
                        },
                        description: {
                          value:
                            'a passionate description of collectiveoffer 98',
                          matchLevel: 'none',
                          matchedWords: [],
                        },
                      },
                      offerer: {
                        name: {
                          value: 'eac_pending_bank_informations',
                          matchLevel: 'none',
                          matchedWords: [],
                        },
                      },
                      venue: {
                        name: {
                          value:
                            'reimbursementPoint eac_pending_bank_informations',
                          matchLevel: 'none',
                          matchedWords: [],
                        },
                        publicName: {
                          value:
                            'reimbursementPoint eac_pending_bank_informations',
                          matchLevel: 'none',
                          matchedWords: [],
                        },
                      },
                    },
                  },
                ],
                nbHits: 1,
                page: 0,
                nbPages: 1,
                hitsPerPage: 20,
                exhaustiveNbHits: true,
                exhaustiveTypo: true,
                exhaustive: {
                  nbHits: true,
                  typo: true,
                },
                query: '',
                params: '',
                index: 'testing-collective-offers',
                renderingContent: {},
                processingTimeMS: 2,
                processingTimingsMS: {
                  _request: {
                    roundTrip: 13,
                  },
                  afterFetch: {
                    format: {
                      total: 1,
                    },
                  },
                  getIdx: {
                    load: {
                      total: 1,
                    },
                    total: 2,
                  },
                  total: 2,
                },
                serverTimeMS: 4,
              },
              {
                hits: [
                  {
                    offer: {
                      name: 'offer 280 pour eac_pending_bank_informations template request',
                      interventionArea: ['2A', '2B'],
                    },
                    venue: {
                      name: 'reimbursementPoint eac_pending_bank_informations',
                      publicName:
                        'reimbursementPoint eac_pending_bank_informations',
                    },
                    isTemplate: true,
                    objectID: `T-${offerId}`,
                  },
                ],
                nbHits: 1,
                page: 0,
                nbPages: 19,
                hitsPerPage: 8,
                exhaustiveNbHits: true,
                exhaustiveTypo: true,
                exhaustive: {
                  nbHits: true,
                  typo: true,
                },
                query: '',
                params:
                  'aroundLatLng=48.8566%2C%202.3522&aroundRadius=30000000&attributesToHighlight=%5B%5D&attributesToRetrieve=%5B%22objectID%22%2C%22offer.dates%22%2C%22offer.name%22%2C%22offer.thumbUrl%22%2C%22venue.name%22%2C%22venue.publicName%22%2C%22isTemplate%22%2C%22offer.interventionArea%22%5D&clickAnalytics=true&distinct=false&facetFilters=%5B%5B%22offer.educationalInstitutionUAICode%3Aall%22%2C%22offer.educationalInstitutionUAICode%3A0910620E%22%5D%5D&filters=offer.eventAddressType%3AoffererVenue%3Cscore%3D3%3E%20OR%20offer.eventAddressType%3Aschool%3Cscore%3D2%3E%20OR%20offer.eventAddressType%3Aother%3Cscore%3D1%3E&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=8&page=0&query=',
                index: 'testing-collective-offers',
                queryID: '324dafe3bdf5ec1e8bfeb03f89044fc0',
                renderingContent: {},
                processingTimeMS: 1,
                processingTimingsMS: {
                  _request: {
                    roundTrip: 13,
                  },
                },
                serverTimeMS: 5,
              },
            ],
          },
        })
    ).as('searchOfferTemplate')
  })

  it('It should put an offer in favorite', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    cy.findAllByTestId('spinner').should('not.exist')

    // I add first offer to favorites
    cy.findByText(offerName).parent().click()
    cy.intercept({
      method: 'POST',
      url: '/adage-iframe/logs/fav-offer/',
    }).as('fav-offer')
    cy.findByTestId('favorite-inactive').click()
    cy.wait('@fav-offer', { responseTimeout: 30 * 1000 })
      .its('response.statusCode')
      .should('eq', 204)

    cy.findByTestId('global-notification-success').should(
      'contain',
      'Ajouté à vos favoris'
    )

    // Then the first offer should be added to favorites
    cy.contains('Mes Favoris').click()
    cy.contains(offerName).should('be.visible')

    // Then we can remove it from favorites
    cy.intercept({
      method: 'DELETE',
      url: '/adage-iframe/collective/template/**/favorites',
    }).as('delete_fav')
    cy.findByTestId('favorite-active').click()
    cy.wait('@delete_fav').its('response.statusCode').should('eq', 204)
    cy.findByTestId('global-notification-success').should(
      'contain',
      'Supprimé de vos favoris'
    )
  })

  it('Should redirect to adage discovery', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // Then the iframe should be displayed correctly
    cy.url().should('include', '/decouverte')
    cy.findAllByRole('link', { name: 'Découvrir (Onglet actif)' })
      .first()
      .should('have.attr', 'aria-current', 'page')

    // Then the banner is displayed
    cy.get('[class^=_discovery-banner]').contains(
      'Découvrez la part collective du pass Culture'
    )
  })

  it('Should redirect to a page dedicated to the offer with an active header on the discovery tab', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // I click on an offer
    cy.findByText(offerName).parent().click()

    // Then the iframe should be displayed correctly
    cy.url().should('include', '/decouverte')
    cy.findAllByRole('link', { name: 'Découvrir (Onglet actif)' })
      .first()
      .should('have.attr', 'aria-current', 'page')
  })

  it('Should redirect to search page with filtered venue on click in venue card', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // When I click on venue
    cy.findByText('Mon lieu collectif').parent().click()

    // Then the iframe search page should be displayed correctly
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    // Venue filter should be there
    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
  })

  it('Should redirect to search page with filtered domain on click in domain card', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // When I select first card domain
    cy.findAllByText('Danse').first().click()

    // Then the iframe search page should be displayed correctly
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    // And the "Danse" button should be displayed
    cy.get('button').contains('Danse')
  })

  it('Should not keep filters after page change', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // When I click on venue
    cy.findByText('Mon lieu collectif').parent().click()

    // Then the iframe search page should be displayed correctly
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    // When I go back to search page
    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
    cy.findByRole('link', { name: 'Découvrir' }).click()
    cy.findByRole('link', { name: 'Rechercher' }).click()

    // The filter has disappear
    cy.findByText('Lieu : Mon lieu collectif').should('not.exist')
  })

  it('Should not keep filter venue after page change', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // When I click on venue
    cy.findByText('Mon lieu collectif').parent().click()

    // Then the iframe search page should be displayed correctly
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    // When I go back to search page
    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
    cy.findByRole('link', { name: 'Découvrir' }).click()
    cy.findByRole('link', { name: 'Rechercher' }).click()

    // The filter has disappear
    cy.findByText('Lieu : Mon lieu collectif').should('not.exist')
  })

  it('Should save view type in search page', () => {
    // I open adage iframe at search page
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    // Then offer descriptions are displayed
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('exist')

    // When I chose grid view
    cy.findAllByTestId('toggle-button').click()

    // Then offer descriptions are not displayed
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('not.exist')

    // I put my offer in favorite
    cy.findByTestId('favorite-inactive').click()

    // And I go to "Mes Favoris" menu
    cy.contains('Mes Favoris').click()

    // Then offer descriptions are displayed
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('exist')

    // And I go to "Rechercher" menu
    cy.contains('Rechercher').click()

    // Then offer descriptions are not displayed
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('not.exist')
  })

  it('Should save filter when page changing', () => {
    // I open adage iframe
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    // When I choose my filters
    cy.findByText('Mon lieu collectif').parent().click()

    cy.wait(500) // Click on "Domaine artistique" is too fast waiting api is not enough
    cy.findByRole('button', { name: 'Domaine artistique' }).click()
    cy.findByLabelText('Danse').click()
    cy.findAllByRole('button', { name: 'Rechercher' }).first().click()

    cy.findByRole('button', { name: 'Format' }).click()
    cy.findByLabelText('Concert').click()
    cy.findAllByRole('button', { name: 'Rechercher' }).first().click()

    // And I go to "Mes Favoris" menu
    cy.contains('Mes Favoris').click()

    // And I go to "Rechercher" menu
    cy.contains('Rechercher').click()

    // Filters are selected',
    cy.findByRole('button', { name: 'Format (1)' }).click()
    cy.findByLabelText('Concert').should('be.checked')

    cy.findByRole('button', { name: 'Domaine artistique (1)' }).click()
    cy.findByLabelText('Danse').should('be.checked')

    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
  })

  it('Should save page when navigating the iframe', () => {
    // I open adage iframe at search page
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    // I go the the next page of searched offers
    cy.findByTestId('next-page-button').click()
    cy.findByText('Page 2/19').should('be.visible')

    // And I go to "Mes Favoris" menu
    cy.contains('Mes Favoris').click()
    // And I go to "Rechercher" menu
    cy.contains('Rechercher').click()

    // page has not changed
    cy.findByText('Page 2/19').should('be.visible')
  })
})
