import { shouldStatusBarBeColored } from '../shouldStatusBarBeColored'

describe('should status bar be colored', () => {
  describe('when user is on a page without a pink header', () => {
    it('should return false', () => {
      // given
      const discoveryPath = '/decouverte/YTRE/FD'

      // when
      const isStatusBarPink = shouldStatusBarBeColored(discoveryPath)

      // then
      expect(isStatusBarPink).toBe(false)
    })
  })

  describe('when user is on a page with a pink header', () => {
    it('should return true', () => {
      // given
      const pathsWithPinkHeader = [
        '/accueil',
        '/recherche/criteres-categorie',
        '/recherche/criteres-localisation',
        '/recherche/criteres-localisation/place',
        '/recherche/criteres-tri',
        '/recherche/resultats/tri',
        '/recherche/resultats/details/N9?mots-cles=&autour-de=non&tri=&categories=&latitude=null&longitude=null',
        '/recherche/resultats/filtres',
        '/recherche/resultats/filtres/localisation',
        '/recherche/resultats/filtres/localisation/place',
        '/reservations/details/BR',
        '/reservations/details/BR/qrcode',
        '/reservations/details/C8/reservation/annulation/confirmation',
        '/favoris/details/4L/V12',
        '/favoris/details/AGJK/BCD3/reservation',
        '/favoris/details/AGJK/BCD3/reservation/KL/annulation/confirmation',
        '/profil/informations',
        '/profil/mot-de-passe',
        '/profil/mentions-legales',
      ]

      pathsWithPinkHeader.forEach(path => {
        // when
        const isStatusBarPink = shouldStatusBarBeColored(path)
        // then
        expect(isStatusBarPink).toBe(true)
      })
    })
  })
})
