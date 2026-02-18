import * as routerUtils from '@/app/AppRouter/utils'
import { makeCurrentRoute } from '@/commons/utils/factories/routeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { getMainHeading } from '../getMainHeading'

describe('getMainHeading', () => {
  const fakeVenue = makeGetVenueResponseModel({
    id: 1,
    publicName: 'Mon lieu culturel',
  })

  it('should return legacy heading on /accueil when new homepage is disabled', () => {
    vi.spyOn(routerUtils, 'isNewHomepageEnabled').mockReturnValue(false)

    const result = getMainHeading(makeCurrentRoute('/accueil'), fakeVenue)

    expect(result).toBe('Bienvenue sur votre espace partenaire')
  })

  it('should return undefined for an unknown pathname', () => {
    vi.spyOn(routerUtils, 'isNewHomepageEnabled').mockReturnValue(false)

    const result = getMainHeading(makeCurrentRoute('/unknown'), fakeVenue)

    expect(result).toBeUndefined()
  })

  describe('WIP_SWITCH_VENUE and WIP_ENABLE_NEW_PRO_HOME feature flags ', () => {
    it('should return venue public name heading on /accueil when new homepage is enabled', () => {
      vi.spyOn(routerUtils, 'isNewHomepageEnabled').mockReturnValue(true)

      const result = getMainHeading(makeCurrentRoute('/accueil'), fakeVenue)

      expect(result).toBe('Votre espace Mon lieu culturel')
    })

    it('should return the heading for /offres/collectives', () => {
      vi.spyOn(routerUtils, 'isNewHomepageEnabled').mockReturnValue(true)

      const result = getMainHeading(
        makeCurrentRoute('/offres/collectives'),
        fakeVenue
      )

      expect(result).toBe('Offres réservables')
    })

    it('should return the heading for /reservations', () => {
      vi.spyOn(routerUtils, 'isNewHomepageEnabled').mockReturnValue(true)

      const result = getMainHeading(
        makeCurrentRoute('/reservations'),
        fakeVenue
      )

      expect(result).toBe('Réservations individuelles')
    })
  })
})
