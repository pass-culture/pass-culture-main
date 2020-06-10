import { isPathWithNavBar } from '../isPathWithNavBar'

describe('when page matching URI contains nav bar', () => {
  it('should return true', () => {
    // Given
    const path = '/path/with/navbar'

    // When
    const pageHasNavBar = isPathWithNavBar(path)

    // Then
    expect(pageHasNavBar).toBe(true)
  })
})

describe('when page matching URI does not contain nav bar', () => {
  it('should return false', () => {
    // Given
    const paths = [
      '/',
      '/reservation',
      '/informations',
      '/mot-de-passe',
      '/mentions-legales',
      '/criteres-tri',
      '/criteres-categorie',
      '/tri',
      '/filtres',
      '/filtres/localisation',
      '/bienvenue',
      '/typeform',
      '/beta',
      '/connexion',
      '/mot-de-passe-perdu',
      '/mot-de-passe-perdu/success?token=ABCDEF',
      '/activation/error',
      '/activation/lien-invalide',
      '/activation/MEFA',
      '/inscription',
    ]

    paths.forEach(path => {
      // When
      const pageHasNavBar = isPathWithNavBar(path)
      // Then
      expect(pageHasNavBar).toBe(false)
    })
  })
})
