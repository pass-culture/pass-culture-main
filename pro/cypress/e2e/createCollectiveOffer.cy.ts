import { addDays, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFound,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Create collective offers', () => {
  let login: string
  let offerDraft: { name: string; venueName: string }
  const newOfferName = 'Ma nouvelle offre collective créée'
  const venueName = 'Mon Lieu 1'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
      (response) => {
        login = response.body.user.email
        offerDraft = response.body.offerDraft
      }
    )
    cy.intercept(
      'GET',
      'http://localhost:5001/collective/educational-domains',
      {
        body: [
          { id: 2, name: 'Danse', nationalPrograms: [] },
          { id: 3, name: 'Architecture', nationalPrograms: [] },
        ],
      }
    ).as('getDomains')

    cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
      'collectiveOffers'
    )
    cy.intercept({ method: 'GET', url: '/offerers/educational*' }).as(
      'educationalOfferers'
    )
  })

  it('I can create an offer with draft status', () => {
    logInAndGoToPage(login, '/offre/creation')

    cy.stepLog({
      message: 'I want to create "Une offre réservable',
    })

    cy.findByText('À un groupe scolaire').click()
    cy.findByText('Étape suivante').click()

    cy.wait('@getDomains')

    cy.findByLabelText('Structure *').select(venueName)

    cy.findByLabelText('Domaines artistiques').click()

    cy.findByLabelText('Architecture').click()
    cy.findByText('Quel est le type de votre offre ?').click()

    cy.findByLabelText('Formats').click()
    cy.findByLabelText('Concert').click()
    cy.findByText('Quel est le type de votre offre ?').click()

    cy.findByLabelText('Titre de l’offre *').type(newOfferName)
    cy.findByLabelText(
      'Décrivez ici votre projet et son interêt pédagogique *'
    ).type('Bookable draft offer')
    cy.findByText('Collège').click()
    cy.findByText('6e').click()
    cy.findByLabelText('Email *').type('example@passculture.app')
    cy.findByLabelText('Email auquel envoyer les notifications *').type(
      'example@passculture.app'
    )

    cy.findByText('Enregistrer et continuer').click()

    const tomorrow = addDays(new Date(), 1)
    const dayAfterTomorrow = addDays(new Date(), 2)

    cy.findByLabelText('Date de début').type(
      format(dayAfterTomorrow, 'yyyy-MM-dd')
    )
    cy.findByLabelText('Horaire').type('18:30')
    cy.findByLabelText('Nombre de participants').type('10')
    cy.findByLabelText('Prix total TTC').type('10')
    cy.findByLabelText('Informations sur le prix').type('description')
    cy.findByLabelText('Date limite de réservation').type(
      format(tomorrow, 'yyyy-MM-dd')
    )

    cy.findByText('Enregistrer et continuer').click()

    cy.findByLabelText('Nom de l’établissement scolaire ou code UAI *').type(
      'COLLEGE 123'
    )
    cy.get('#list-institution')
      .findByText(/COLLEGE 123/)
      .click()
    cy.findByText("Renseignez l'établissement scolaire et l’enseignant").click()

    cy.findByText("Renseignez l'établissement scolaire et l’enseignant").click()

    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Sauvegarder le brouillon et quitter').click()

    cy.findByText('Brouillon sauvegardé dans la liste des offres')

    cy.stepLog({ message: 'I want to see my offer in draft status' })

    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.get('#search-status').click()
    cy.get('#list-status').find('#option-display-DRAFT').click()
    // We click outside the filter to close it
    cy.findByRole('heading', { name: 'Offres collectives' }).click()
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    const expectedResults = [
      [
        '',
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        '',
        newOfferName,
        `${format(dayAfterTomorrow, 'dd/MM/yyyy')}18h30`,
        venueName,
        'COLLEGE 123',
        'brouillon',
      ],
      [
        '',
        '',
        '',
        offerDraft.name,
        'Toute l’année scolaire',
        offerDraft.venueName,
        'DE LA TOUR',
        'brouillon',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)

    cy.stepLog({ message: 'I want to change my offer to published status' })

    cy.findAllByTestId('offer-item-row')
      .eq(0)
      .within(() => cy.findByRole('link', { name: newOfferName }).click())

    cy.wait('@educationalOfferers')

    cy.findByRole('link', { name: '5 Aperçu' }).click()
    cy.findByText('Publier l’offre').click()
    cy.findByText('Voir mes offres').click()

    cy.stepLog({ message: 'I want to see my offer in published status' })

    cy.url().should('contain', '/offres/collectives')

    cy.findByText('Réinitialiser les filtres').click()
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type(newOfferName)
    cy.findByText('Rechercher').click()

    const expectedNewResults = [
      [
        '',
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        '',
        newOfferName,
        `${format(dayAfterTomorrow, 'dd/MM/yyyy')}18h30`,
        venueName,
        'COLLEGE 123',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedNewResults)
  })

  it('I can create a bookable offer with specific address when FF OA is active', () => {
    cy.setFeatureFlags([
      { name: 'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE', isActive: true },
    ])

    logInAndGoToPage(login, '/offre/creation')

    cy.stepLog({
      message: 'I want to create "Une offre réservable',
    })

    cy.findByText('À un groupe scolaire').click()
    cy.findByText('Étape suivante').click()

    cy.wait('@getDomains')

    cy.findByLabelText('Structure *').select(venueName)

    cy.findByLabelText('Domaines artistiques').click()

    cy.findByLabelText('Architecture').click()
    cy.findByText('Quel est le type de votre offre ?').click()

    cy.findByLabelText('Formats').click()
    cy.findByLabelText('Concert').click()
    cy.findByText('Quel est le type de votre offre ?').click()

    cy.findByLabelText('Titre de l’offre *').type(newOfferName)
    cy.findByLabelText(
      'Décrivez ici votre projet et son interêt pédagogique *'
    ).type('Bookable draft offer')
    cy.findByLabelText('Autre adresse').click()
    cy.findByLabelText('Adresse postale *').type('10 Rue')
    cy.get('[data-testid="list"] li').first().click()
    cy.findByText('Collège').click()
    cy.findByText('6e').click()
    cy.findByLabelText('Email *').type('example@passculture.app')
    cy.findByLabelText('Email auquel envoyer les notifications *').type(
      'example@passculture.app'
    )

    cy.findByText('Enregistrer et continuer').click()

    const tomorrow = addDays(new Date(), 1)
    const dayAfterTomorrow = addDays(new Date(), 2)

    cy.findByLabelText('Date de début').type(
      format(dayAfterTomorrow, 'yyyy-MM-dd')
    )
    cy.findByLabelText('Horaire').type('18:30')
    cy.findByLabelText('Nombre de participants').type('10')
    cy.findByLabelText('Prix total TTC').type('10')
    cy.findByLabelText('Informations sur le prix').type('description')
    cy.findByLabelText('Date limite de réservation').type(
      format(tomorrow, 'yyyy-MM-dd')
    )

    cy.findByText('Enregistrer et continuer').click()

    cy.findByLabelText('Nom de l’établissement scolaire ou code UAI *').type(
      'COLLEGE 123'
    )
    cy.get('#list-institution')
      .findByText(/COLLEGE 123/)
      .click()
    cy.findByText("Renseignez l'établissement scolaire et l’enseignant").click()

    cy.findByText("Renseignez l'établissement scolaire et l’enseignant").click()

    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Sauvegarder le brouillon et quitter').click()

    cy.findByText('Brouillon sauvegardé dans la liste des offres')

    cy.stepLog({ message: 'I want to see my offer in draft status' })

    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.get('#search-status').click()
    cy.get('#list-status').find('#option-display-DRAFT').click()
    // We click outside the filter to close it
    cy.findByRole('heading', { name: 'Offres collectives' }).click()
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    const expectedResults = [
      [
        '',
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        '',
        newOfferName,
        `${format(dayAfterTomorrow, 'dd/MM/yyyy')}18h30`,
        venueName,
        'COLLEGE 123',
        'brouillon',
      ],
      [
        '',
        '',
        '',
        offerDraft.name,
        'Toute l’année scolaire',
        offerDraft.venueName,
        'DE LA TOUR',
        'brouillon',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)

    cy.stepLog({ message: 'I want to change my offer to published status' })

    cy.findAllByTestId('offer-item-row')
      .eq(0)
      .within(() => cy.findByRole('link', { name: newOfferName }).click())

    cy.wait('@educationalOfferers')

    cy.findByRole('link', { name: '5 Aperçu' }).click()
    cy.findByText('Publier l’offre').click()
    cy.findByText('Voir mes offres').click()

    cy.stepLog({ message: 'I want to see my offer in published status' })

    cy.url().should('contain', '/offres/collectives')

    cy.findByText('Réinitialiser les filtres').click()
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type(newOfferName)
    cy.findByText('Rechercher').click()

    const expectedNewResults = [
      [
        '',
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        '',
        newOfferName,
        `${format(dayAfterTomorrow, 'dd/MM/yyyy')}18h30`,
        venueName,
        'COLLEGE 123',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedNewResults)
  })
})
