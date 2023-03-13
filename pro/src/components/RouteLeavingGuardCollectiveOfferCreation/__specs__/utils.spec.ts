import { shouldBlockNavigation } from '../utils'

describe('components | RouteLeavingGuardCollectiveOfferCreation', () => {
  describe('when following creation flow', () => {
    it('should not display confirmation modal when following creation flow', async () => {
      //   jest.spyOn(routerCompat, 'useLocation').mockReturnValueOnce({
      //     pathname: '/offre/creation/collectif',
      //   })
      const fromCreationToStocks = shouldBlockNavigation({
        currentLocation: { pathname: '/offre/creation/collectif' },
        nextLocation: { pathname: '/offre/AE/collectif/stocks' },
      })

      expect(fromCreationToStocks).toStrictEqual({ shouldBlock: false })

      const fromStockToVisibility = shouldBlockNavigation({
        currentLocation: { pathname: '/offre/AE/collectif/stocks' },
        nextLocation: { pathname: '/offre/AE/collectif/visibilite' },
      })

      expect(fromStockToVisibility).toStrictEqual({ shouldBlock: false })

      const fromVisibilityToRecap = shouldBlockNavigation({
        currentLocation: { pathname: '/offre/AE/collectif/visibilite' },
        nextLocation: {
          pathname: '/offre/AE/collectif/creation/recapitulatif',
        },
      })

      expect(fromVisibilityToRecap).toStrictEqual({ shouldBlock: false })

      const fromRecapToConfirmation = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/creation/recapitulatif',
        },
        nextLocation: {
          pathname: '/offre/AE/collectif/confirmation',
        },
      })

      expect(fromRecapToConfirmation).toStrictEqual({ shouldBlock: false })
    })

    it('should not display confirmation modal when following template creation flow', async () => {
      const fromCreationToRecap = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/creation/collectif',
        },
        nextLocation: {
          pathname: '/offre/AE/collectif/creation/recapitulatif',
        },
      })

      expect(fromCreationToRecap).toStrictEqual({ shouldBlock: false })

      const fromRecapToConfirmation = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/creation/recapitulatif',
        },
        nextLocation: {
          pathname: '/offre/AE/collectif/confirmation',
        },
      })

      expect(fromRecapToConfirmation).toStrictEqual({ shouldBlock: false })
    })

    it('should display confirmation modal when leaving offer creation', async () => {
      const fromCreationToAccueil = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/creation/collectif',
        },
        nextLocation: {
          pathname: '/',
        },
      })

      expect(fromCreationToAccueil).toStrictEqual({ shouldBlock: true })
    })

    it('should display confirmation modal when leaving stock creation', async () => {
      const fromStockToCreation = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/stocks',
        },
        nextLocation: {
          pathname: '/offre/creation/collectif',
        },
      })

      expect(fromStockToCreation).toStrictEqual({ shouldBlock: false })

      const fromCreationToAccueil = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/creation/collectif',
        },
        nextLocation: {
          pathname: '/',
        },
      })

      expect(fromCreationToAccueil).toStrictEqual({ shouldBlock: true })
    })

    it('should display confirmation modal when leaving visibility creation', async () => {
      const fromVisibilityToAccueil = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/visibilite',
        },
        nextLocation: {
          pathname: '/',
        },
      })

      expect(fromVisibilityToAccueil).toStrictEqual({ shouldBlock: true })
    })

    it('should display confirmation modal when leaving summary creation', async () => {
      const fromRecapToVisibility = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/creation/recapitulatif',
        },
        nextLocation: {
          pathname: '/offre/AE/collectif/visibilite',
        },
      })

      expect(fromRecapToVisibility).toStrictEqual({ shouldBlock: false })

      const fromVisibilityToAccueil = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/visibilite',
        },
        nextLocation: {
          pathname: '/',
        },
      })

      expect(fromVisibilityToAccueil).toStrictEqual({ shouldBlock: true })
    })

    it('should not display confirmation modal when leaving confirmation page', async () => {
      const fromConfirmationToAccueil = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/confirmation',
        },
        nextLocation: {
          pathname: '/',
        },
      })

      expect(fromConfirmationToAccueil).toStrictEqual({
        redirectPath: null,
        shouldBlock: false,
      })
    })

    it('should not display confirmation modal when going from stocks to offer creation', async () => {
      const fromStockToCreation = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/stocks',
        },
        nextLocation: {
          pathname: '/offre/creation/collectif',
        },
      })

      expect(fromStockToCreation).toStrictEqual({
        shouldBlock: false,
      })
    })

    it('should not display confirmation modal when going from stocks to offer creation with offer id in url', async () => {
      const fromStockToCreation = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/stocks',
        },
        nextLocation: {
          pathname: '/offre/collectif/AE/creation',
        },
      })

      expect(fromStockToCreation).toStrictEqual({
        shouldBlock: false,
      })
    })

    it('should not display confirmation modal when going from visibility to stocks', () => {
      const fromVisibilityToStock = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/visibilite',
        },
        nextLocation: {
          pathname: '/offre/AE/collectif/stocks',
        },
      })

      expect(fromVisibilityToStock).toStrictEqual({
        shouldBlock: false,
      })
    })

    it('should not display confirmation modal when going from visibility to offer creation', () => {
      const fromVisibilityToCreation = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/visibilite',
        },
        nextLocation: {
          pathname: '/offre/collectif/AE/creation',
        },
      })

      expect(fromVisibilityToCreation).toStrictEqual({
        shouldBlock: false,
      })
    })

    it('should not display confirmation modal when going from confirmation to recapitulatif', () => {
      const fromConfirmationToRecap = shouldBlockNavigation({
        currentLocation: {
          pathname: '/offre/AE/collectif/confirmation',
        },
        nextLocation: {
          pathname: '/offre/AE/collectif/creation/recapitulatif',
        },
      })

      expect(fromConfirmationToRecap).toStrictEqual({
        redirectPath: '/offres/collectives',
        shouldBlock: false,
      })
    })
  })
})
