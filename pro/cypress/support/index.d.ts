declare namespace Cypress {
  interface Chainable {
    login(email: string, password: string, redirectUrl?: string): Chainable
    setFeatureFlags(features: Feature[]): Chainable
  }
}

interface Feature {
  name: string
  isActive: boolean
}
