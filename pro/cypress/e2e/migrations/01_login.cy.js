describe('Login Test with HTTP Request', () => {

    let login = '';
    let password = 'user@AZERTY123'

    before(() => {
        cy.visit('/connexion')
        cy.request({
            method: 'GET',
            url: 'http://localhost:5001/sandboxes/pro_01_create_pro_user/create_pro_user_with_venue_bank_account_and_userofferer',
        }).then((response) => {
            login = response.body.user.email
        });
    })

    it('Should fill out the login form', () => {
        expect(true).to.equal(true)
        cy.login({ email: login, password: password, redirectUrl: "/parcours-inscription" })
        cy.findAllByTestId('spinner').should('not.exist')
        cy.findByText('Finalisez votre inscription')
    });

});