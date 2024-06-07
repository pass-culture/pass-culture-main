import { When, Then, Given } from '@badeball/cypress-cucumber-preprocessor'

let bookinText: string

Given('I display offers', () => {
    cy.findByText('Afficher').click()
})

When('I search for {string} with name {string}', (type: string, name: string) => {
    bookinText = name

    cy.findByText('Afficher').click()

    // éléments non accessibles, getByRole() marche pas, on a utilisé du cypress natif
    cy.get('*[class^="_omnisearch-container"]').within(() => {
        cy.get('select').select(type)
        cy.get('#text-filter-input').type(bookinText)
    })
})

When('I search for Offre with name {string}', (name: string) => {
    bookinText = name

    cy.findByText('Afficher').click()

    // éléments non accessibles, getByRole() marche pas, on a utilisé du cypress natif
    cy.get('*[class^="_omnisearch-container"]').within(() => {
        cy.get('select').select('Offre')
        cy.get('#text-filter-input').type(bookinText)
    })
})

When('I search for Établissement with name {string}', (name: string) => {
    bookinText = name

    cy.findByText('Afficher').click()

    // éléments non accessibles, getByRole() marche pas, on a utilisé du cypress natif
    cy.get('*[class^="_omnisearch-container"]').within(() => {
        cy.get('select').select('Établissement')
        cy.get('#text-filter-input').type(bookinText)
    })
})

When('I search for Numéro de réservation with number {string}', (name: string) => {
    bookinText = name

    cy.findByText('Afficher').click()

    // éléments non accessibles, getByRole() marche pas, on a utilisé du cypress natif
    cy.get('*[class^="_omnisearch-container"]').within(() => {
        cy.get('select').select('Numéro de réservation')
        cy.get('#text-filter-input').type(bookinText)
    })
})

Then('I should see {string} results', (value: string) => {
    cy.get('table').contains(bookinText)
        .should('have.length', value)
})

Then('I should see my Offre', () => {
    cy.get('*[class^="_booking-offer-name"]').contains(bookinText)
})

Then('I should see my Établissement', () => {
    cy.get('table').contains(bookinText)
        .should('exist')
})