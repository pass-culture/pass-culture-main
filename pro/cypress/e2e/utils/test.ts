// // @P0
// // Feature: ADAGE discovery

// //   Background:
// //     Given I go to adage login page with valid token

// //   Scenario: It should put an offer in favorite
// //     When I open adage iframe
// //     And I add first offer to favorites
// //     Then the first offer should be added to favorites
// //     And the first favorite is unselected

// describe('ADAGE discovery', () => {
//   beforeEach(() => {
//     cy.getFakeAdageToken()
//   })

//   it('should successfully open adage iframe', () => {
//     const adageToken = Cypress.env('adageToken')
//     cy.visit('/connexion')
//     cy.intercept({
//       method: 'GET',
//       url: '/adage-iframe/playlists/local-offerers',
//     }).as('local_offerers')
//     cy.intercept({
//       method: 'GET',
//       url: '/features',
//     }).as('features')

//     cy.visit(`/adage-iframe?token=${adageToken}`)

//     cy.findAllByTestId('spinner').should('not.exist')

//     cy.wait(['@local_offerers', '@features'], {
//       responseTimeout: 30 * 1000,
//     }).then((interception) => {
//       if (interception[0].response) {
//         expect(interception[0].response.statusCode).to.equal(200)
//       }
//       if (interception[1].response) {
//         expect(interception[1].response.statusCode).to.equal(200)
//       }
//     })
//     cy.findAllByTestId('spinner').should('not.exist')
//     cy.wait(500)
//   })
// })
