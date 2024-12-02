import { expectOffersOrBookingsAreFound, logAndGoToPage } from '../support/helpers.ts'

describe('Collaborator list feature', () => {
  let login: string
  const offerName = 'Mon offre collective en brouillon'
  const venueName = "Mon Lieu 1"

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.intercept(
        'GET',
        'http://localhost:5001/collective/educational-domains',
        {
          body: [
            { id: 1, name: 'Danse' },
            { id: 2, name: 'Architecture' },
          ]
        }
      ).as('getDomains')

      cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
        'collectiveOffers'
      )
      cy.intercept({method: 'GET', url: '/offerers/educational*'}).as('educationalOfferers')

    cy.setFeatureFlags([
      { name: 'ENABLE_COLLECTIVE_NEW_STATUSES', isActive: true },
    ])
  })

  it('I can create an offer with draft status', () => {
    logAndGoToPage(login, '/offre/creation')

    cy.stepLog({
        message: 'I want to create "Une offre réservable',
      })

      cy.findByText('À un groupe scolaire').click()
      cy.findByText('Étape suivante').click()

      cy.wait('@getDomains')

      cy.findByLabelText('Lieu *').select(venueName)

      cy.findByLabelText('Domaine artistique et culturel *').click()

      cy.get('#list-domains').find('#option-display-2').click()
      cy.findByText('Type d’offre').click()

      cy.findByLabelText('Format *').click()
      cy.get('#list-formats').find('#option-display-Concert').click()
      cy.findByText('Type d’offre').click()
      
      cy.findByLabelText('Titre de l’offre *').type(offerName)
      cy.findByLabelText('Description *').type(
        'Bookable draft offer'
      )
      cy.findByText('Collège - 6e').click()
      cy.findByLabelText('Email *').type('example@passculture.app')
      cy.findByLabelText('Email auquel envoyer les notifications *').type('example@passculture.app')

      cy.findByText('Enregistrer et continuer').click()

      cy.findByLabelText('Date de début *').type('2025-05-10')
      cy.findByLabelText('Horaire *').type('18:30')
      cy.findByLabelText('Nombre de participants *').type('10')
      cy.findByLabelText('Prix total TTC *').type('10')
      cy.findByLabelText('Informations sur le prix *').type('description')
      cy.findByLabelText('Date limite de réservation *').type('2025-05-09')

      cy.findByText('Enregistrer et continuer').click()

      cy.findByLabelText('Nom de l’établissement scolaire ou code UAI *').type('COLLEGE')
      cy.get('#list-institution').find('#option-display-1').click()
      cy.findByText('Établissement scolaire et enseignant').click()

      cy.findByText('Enregistrer et continuer').click()
      cy.findByText('Enregistrer et continuer').click()
      cy.findByText('Sauvegarder le brouillon et quitter').click()

      cy.findByText('Brouillon sauvegardé dans la liste des offres')

      cy.stepLog({ message: 'I want to see my offer in draft status' })

      cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

      cy.get('#search-status').click()
      cy.get('#list-status').find('#option-display-DRAFT').click()
      cy.findByText('Offres collectives').click()

      cy.findByText('Rechercher').click()
      cy.wait('@collectiveOffers')

      const expectedResults = [
        ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
        [
          '',
          '',
          offerName,
          venueName,
          'COLLEGE 123',
          'brouillon',
        ],
        []
      ]
  
      expectOffersOrBookingsAreFound(expectedResults)

      cy.stepLog({ message: 'I want to change my offer to published status' })

      cy.findByRole('link', {name: offerName}).click()

      cy.wait('@educationalOfferers')
      
      cy.findByRole('link', {name: '5 Aperçu'}).click()
      cy.findByText('Publier l’offre').click()
      cy.findByText('Voir mes offres').click()

      cy.stepLog({ message: 'I want to see my offer in published status' })

      cy.url().should('contain', '/offres/collectives')

      cy.findByPlaceholderText('Rechercher par nom d’offre').type(
        offerName
      )
      cy.findByText('Rechercher').click()

      const expectedNewResults = [
        ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
        [
          '',
          '',
          offerName,
          venueName,
          'COLLEGE 123',
          'publiée',
        ],
        []
      ]
  
      expectOffersOrBookingsAreFound(expectedNewResults)
  })
})
