describe('ADAGE discovery', () => {
  let offerId: number
  const offerName = 'Mon offre collective'

  beforeEach(() => {
    cy.stepLog({ message: 'I go to adage login page with valid token' })
    cy.visit('/connexion')
    cy.getFakeAdageToken()
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_adage_environment',
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
    cy.intercept({
      method: 'DELETE',
      url: '/adage-iframe/collective/template/**/favorites',
    }).as('delete_fav')
    cy.intercept({
      method: 'POST',
      url: '/adage-iframe/logs/fav-offer/',
    }).as('fav-offer')
    cy.intercept({
      method: 'POST',
      url: '/adage-iframe/logs/catalog-view',
    }).as('catalogView')
  })

  it('It should put an offer in favorite', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')

    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)
    cy.wait('@catalogView').its('response.statusCode').should('eq', 204)
    cy.findAllByTestId('spinner').should('not.exist')
    cy.findByTestId('offer-listitem').contains('Mon offre collective')

    cy.stepLog({ message: 'I add first offer to favorites' })
    cy.findByText(offerName).parent().click()
    cy.findByTestId('favorite-inactive').click()
    cy.wait('@fav-offer', { responseTimeout: 30 * 1000 })
      .its('response.statusCode')
      .should('eq', 204)
    cy.findByTestId('global-notification-success').should(
      'contain',
      'Ajouté à vos favoris'
    )

    cy.stepLog({ message: 'the first offer should be added to favorites' })
    cy.contains('Mes Favoris').click()
    cy.contains(offerName).should('be.visible')

    cy.stepLog({ message: 'we can remove it from favorites' })
    cy.findByTestId('favorite-active').click()
    cy.wait('@delete_fav').its('response.statusCode').should('eq', 204)
    cy.findByTestId('global-notification-success').should(
      'contain',
      'Supprimé de vos favoris'
    )
  })

  it('It should redirect to adage discovery', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'the iframe should be displayed correctly' })
    cy.url().should('include', '/decouverte')
    cy.findAllByRole('link', { name: 'Découvrir (Onglet actif)' })
      .first()
      .should('have.attr', 'aria-current', 'page')

    cy.stepLog({ message: 'the banner is displayed' })
    cy.get('[class^=_discovery-banner]').contains(
      'Découvrez la part collective du pass Culture'
    )
  })

  it('It should redirect to a page dedicated to the offer with an active header on the discovery tab', () => {
    // I open adage iframe
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'I click on an offer' })
    cy.findByText(offerName).parent().click()

    cy.stepLog({ message: 'the iframe should be displayed correctly' })
    cy.url().should('include', '/decouverte')
    cy.findAllByRole('link', { name: 'Découvrir (Onglet actif)' })
      .first()
      .should('have.attr', 'aria-current', 'page')
  })

  it('It should redirect to search page with filtered venue on click in venue card', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'I click on venue' })
    cy.findByText('Mon lieu collectif').parent().click()

    cy.stepLog({
      message: 'the iframe search page should be displayed correctly',
    })
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.stepLog({ message: 'Venue filter should be there' })
    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
  })

  it('It should redirect to search page with filtered domain on click in domain card', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'I select first card domain' })
    cy.findAllByText('Danse').first().click()

    cy.stepLog({
      message: 'the iframe search page should be displayed correctly',
    })
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.stepLog({ message: 'the "Danse" button should be displayed' })
    cy.get('button').contains('Danse')
  })

  it('It should not keep filters after page change', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'I click on venue' })
    cy.findByText('Mon lieu collectif').parent().click()

    cy.stepLog({
      message: 'the iframe search page should be displayed correctly',
    })
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.stepLog({ message: 'I go back to search page' })
    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
    cy.findByRole('link', { name: 'Découvrir' }).click()
    cy.findByRole('link', { name: 'Rechercher' }).click()

    cy.stepLog({ message: 'The filter has disappear' })
    cy.findByText('Lieu : Mon lieu collectif').should('not.exist')
  })

  it('It should not keep filter venue after page change', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'I click on venue' })
    cy.findByText('Mon lieu collectif').parent().click()

    cy.stepLog({
      message: 'the iframe search page should be displayed correctly',
    })
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher (Onglet actif)' }).should(
      'have.attr',
      'aria-current',
      'page'
    )

    cy.stepLog({ message: 'I go back to search page' })
    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
    cy.findByRole('link', { name: 'Découvrir' }).click()
    cy.findByRole('link', { name: 'Rechercher' }).click()

    cy.stepLog({ message: 'The filter has disappear' })
    cy.findByText('Lieu : Mon lieu collectif').should('not.exist')
  })

  it('It should save view type in search page', () => {
    cy.stepLog({ message: 'I open adage iframe at search page' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    cy.stepLog({ message: 'offer descriptions are displayed' })
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('exist')

    cy.stepLog({ message: 'I chose grid view' })
    cy.findAllByTestId('toggle-button').click()

    cy.stepLog({ message: 'offer descriptions are not displayed' })
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('not.exist')

    cy.stepLog({ message: 'I put my offer in favorite' })
    cy.findByTestId('favorite-inactive').click()

    cy.stepLog({ message: 'I go to "Mes Favoris" menu' })
    cy.contains('Mes Favoris').click()

    cy.stepLog({ message: 'offer descriptions are displayed' })
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('exist')

    cy.stepLog({ message: 'I go to "Rechercher" menu' })
    cy.contains('Rechercher').click()

    cy.stepLog({ message: 'offer descriptions are not displayed' })
    cy.findAllByTestId('offer-listitem')
    cy.findAllByTestId('offer-description').should('not.exist')
  })

  it('It should save filter when page changing', () => {
    cy.stepLog({ message: 'I open adage iframe' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)

    cy.stepLog({ message: 'I choose my filters' })
    cy.findByText('Mon lieu collectif').parent().click()

    // eslint-disable-next-line cypress/no-unnecessary-waiting
    cy.wait(500) // Click on "Domaine artistique" is too fast waiting api is not enough
    cy.findByRole('button', { name: 'Domaine artistique' }).click()
    cy.findByLabelText('Danse').click()
    cy.findAllByRole('button', { name: 'Rechercher' }).first().click()

    cy.findByRole('button', { name: 'Format' }).click()
    cy.findByLabelText('Concert').click()
    cy.findAllByRole('button', { name: 'Rechercher' }).first().click()

    cy.stepLog({ message: 'I go to "Mes Favoris" menu' })
    cy.contains('Mes Favoris').click()

    cy.stepLog({ message: 'I go to "Rechercher" menu' })
    cy.contains('Rechercher').click()

    cy.stepLog({ message: 'Filters are selected' })
    cy.findByRole('button', { name: 'Format (1)' }).click()
    cy.findByLabelText('Concert').should('be.checked')

    cy.findByRole('button', { name: 'Domaine artistique (1)' }).click()
    cy.findByLabelText('Danse').should('be.checked')

    cy.findByText('Lieu : Mon lieu collectif').should('be.visible')
  })

  it('It should save page when navigating the iframe', () => {
    cy.stepLog({ message: 'I open adage iframe at search page' })
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    cy.stepLog({ message: 'I go the the next page of searched offers' })
    cy.findByTestId('next-page-button').click()
    cy.findByText('Page 2/19').should('be.visible')

    cy.stepLog({ message: 'I go to "Mes Favoris" menu' })
    cy.contains('Mes Favoris').click()

    cy.stepLog({ message: 'I go to "Rechercher" menu' })
    cy.contains('Rechercher').click()

    cy.stepLog({ message: 'page has not changed' })
    cy.findByText('Page 2/19').should('be.visible')
  })
})
