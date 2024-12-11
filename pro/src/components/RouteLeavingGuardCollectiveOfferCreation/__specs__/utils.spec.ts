import type { Location } from 'react-router'

import { shouldBlockNavigation } from '../utils'

describe('components | RouteLeavingGuardCollectiveOfferCreation', () => {
  const cases: {
    description: string
    currentLocation: string
    nextLocation: string
    expectedShouldBlock: boolean
  }[] = [
    {
      description:
        'should not block when following creation flow (from creation to stocks)',
      currentLocation: '/offre/creation/collectif',
      nextLocation: '/offre/AE/collectif/stocks',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when following creation flow (from stocks to visibilite)',
      currentLocation: '/offre/creation/stocks',
      nextLocation: '/offre/AE/collectif/visibilite',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when following creation flow (from visibilite to recapitulatif)',
      currentLocation: '/offre/creation/visibilite',
      nextLocation: '/offre/AE/collectif/recapitulatif',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when following creation flow (from recapitulatif to confirmation)',
      currentLocation: '/offre/creation/recapitulatif',
      nextLocation: '/offre/AE/collectif/confirmation',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when following template creation flow (from creation to recapitulatif)',
      currentLocation: '/offre/creation/collectif',
      nextLocation: '/offre/AE/collectif/creation/recapitulatif',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when following template creation flow (from recapitulatif to confirmation)',
      currentLocation: '/offre/AE/collectif/creation/recapitulatif',
      nextLocation: '/offre/AE/collectif/confirmation',
      expectedShouldBlock: false,
    },
    {
      description: 'should block when leaving offer creation',
      currentLocation: '/offre/creation/collectif',
      nextLocation: '/',
      expectedShouldBlock: true,
    },
    {
      description: 'should block when leaving stock creation',
      currentLocation: '/offre/AE/collectif/stocks',
      nextLocation: '/',
      expectedShouldBlock: true,
    },
    {
      description: 'should block when leaving visibility creation',
      currentLocation: '/offre/AE/collectif/visibilite',
      nextLocation: '/',
      expectedShouldBlock: true,
    },
    {
      description: 'should block when leaving summary creation',
      currentLocation: '/offre/AE/collectif/creation/recapitulatif',
      nextLocation: '/',
      expectedShouldBlock: true,
    },

    {
      description: 'should not block when leaving confirmation page',
      currentLocation: '/offre/AE/collectif/confirmation',
      nextLocation: '/',
      expectedShouldBlock: false,
    },
    {
      description: 'should not block when going from confirmation to summary',
      currentLocation: '/offre/AE/collectif/confirmation',
      nextLocation: '/offre/AE/collectif/creation/recapitulatif',
      expectedShouldBlock: false,
    },
    {
      description: 'should not block when going from summary to visibilite',
      currentLocation: '/offre/AE/collectif/creation/recapitulatif',
      nextLocation: '/offre/AE/collectif/visibilite',
      expectedShouldBlock: false,
    },
    {
      description: 'should not block when going from visibilite to stocks',
      currentLocation: '/offre/AE/collectif/visibilite',
      nextLocation: '/offre/AE/collectif/stocks',
      expectedShouldBlock: false,
    },
    {
      description: 'should not block when going from visibilite to creation',
      currentLocation: '/offre/AE/collectif/visibilite',
      nextLocation: '/offre/collectif/AE/creation',
      expectedShouldBlock: false,
    },
    {
      description: 'should not block when going from stocks to creation page',
      currentLocation: '/offre/AE/collectif/stocks',
      nextLocation: '/offre/creation/collectif',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when going from stocks to creation page with id in url',
      currentLocation: '/offre/AE/collectif/stocks',
      nextLocation: '/offre/collectif/AE/creation',
      expectedShouldBlock: false,
    },
    {
      description:
        'should not block when going from summary to bank account url',
      currentLocation: '/offre/AE/collectif/creation/recapitulatif',
      nextLocation: '/remboursements/informations-bancaires?structure=1E',
      expectedShouldBlock: false,
    },
  ]

  cases.forEach(
    ({ description, currentLocation, nextLocation, expectedShouldBlock }) => {
      it(description, () => {
        expect(
          shouldBlockNavigation({
            currentLocation: { pathname: currentLocation } as Location,
            nextLocation: { pathname: nextLocation } as Location,
          })
        ).toStrictEqual(expectedShouldBlock)
      })
    }
  )
})
