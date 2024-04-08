const locators = {
    lastName: '#lastName',
    firstName: '#firstName',
    email: '#email',
    password: '#password',
    phoneNumber: '#phoneNumber',
    submitButton: 'button[type=submit]',
};

export function typeLastName(userLastName) {
    return cy.get(locators.lastName).type(userLastName);
}

export function typeFirstName(userFirstName) {
    return cy.get(locators.firstName).type(userFirstName);
}

export function typeRandomisedEmail() {
    return cy.get(locators.email).type(`jean${Math.random()}@example.com`);
}

export function typePhoneNumber(userPhoneNumber) {
    return cy.get(locators.phoneNumber).type(userPhoneNumber);
}

export function typePassword(userPassword) {
    return cy.get(locators.password).type(userPassword);
}

export function clickOnSubmit() {
    cy.get(locators.submitButton).click();
}