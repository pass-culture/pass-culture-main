declare namespace Cypress {
  interface Chainable {
    login(params: {
      email: string
      password: string
      redirectUrl?: string
      acceptCookies?: boolean
    }): Chainable
    setFeatureFlags(features: Feature[]): Chainable
    acceptCookies(): Chainable
    getFakeAdageToken(): Chainable
  }
}

interface Feature {
  name: string
  isActive: boolean
}
