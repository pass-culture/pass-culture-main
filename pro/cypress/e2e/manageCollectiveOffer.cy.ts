import {
  logAndGoToPage,
} from '../support/helpers.ts'

describe('Manage collective bookable offer from Draft to In progress', () => {
  let login: string

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
    }).then((response) => {
      login = response.body.user.email
    })
  })

  it('I should bla bla', () => {
    logAndGoToPage(login, '/reservations/collectives')

  })
})
