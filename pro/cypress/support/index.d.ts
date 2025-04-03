declare namespace Cypress {
  interface Chainable {
    /**
     * Activate or disable a feature flag
     *
     * @param {Feature[]} features - An array of `Feature` objects to be updated.
     * Each `Feature` object contains a name and an activation state (`isActive`).
     * @example
     * cy.setFeatureFlags([ { name: 'WIP_ENABLE_MARSEILLE', isActive: true }])
     */
    setFeatureFlags(features: Feature[]): Chainable

    /**
     * This function creates a fake adage token, and returns it as a string
     *
     * @returns a string of the fake adage token
     * @example
     * cy.getFakeAdageToken().then((value) => { adageToken = value })
     * cy.visit(`/adage-iframe/recherche?token=${adageToken}`)
     */
    getFakeAdageToken(): Chainable

    /**
     * Set the slider value of an input of type `range`.
     * Workaround because onChange not triggered for an input type='range' rendered by React
     *
     * @param {number} value
     * @see https://github.com/cypress-io/cypress/issues/1570#issuecomment-891244917
     * @example
     * cy.get('input[type=range]').setSliderValue(1.7)
     */
    setSliderValue(value: number): Chainable<void>

    /**
     * Adds a log in Cypress Cloud and Cypress UI. Usefull to make scenario list of commands more understandable
     *
     * @params {{ message: string }} string containing the
     * @example
     * cy.stepLog({message: 'I want to create an offer'})
     */
    stepLog(params: { message: string }): Chainable

    sandboxCall(
      method: 'GET' | 'POST',
      url: string,
      onRequest: (response: any) => void,
      retry?: boolean
    ): Chainable
  }
}

/**
 * This interface is used to set Feature Flags with a name and a boolean if needs to be activated or not
 *
 * @interface
 *
 * @property {string} name - name of the Feature Flag
 * @property {boolean} isActive - to activate (true) or not (falst)
 */
interface Feature {
  name: string
  isActive: boolean
}
