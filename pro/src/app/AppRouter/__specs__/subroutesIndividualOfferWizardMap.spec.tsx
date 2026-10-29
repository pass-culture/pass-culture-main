import { matchRoutes } from 'react-router'

import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from '../subroutesIndividualOfferWizardMap'

describe('routesIndividualOfferWizard', () => {
  it.each([
    '/offre/individuelle/offer-123/edition/details',
    '/offre/individuelle/offer-123/visibilite',
    '/offre/individuelle/creation/description',
    '/offre/individuelle/offer-123/creation/description',
    '/offre/individuelle/offer-123/edition/description',
    '/offre/individuelle/offer-123/creation/pratiques',
    '/offre/individuelle/offer-123/edition/pratiques',
    '/offre/individuelle/offer-123/creation/localisation',
    '/offre/individuelle/offer-123/edition/localisation',
    '/offre/individuelle/offer-123/creation/media',
    '/offre/individuelle/offer-123/edition/media',
    '/offre/individuelle/offer-123/creation/tarifs',
    '/offre/individuelle/offer-123/edition/tarifs',
    '/offre/individuelle/offer-123/creation/horaires',
    '/offre/individuelle/offer-123/edition/horaires',
    '/offre/individuelle/offer-123/creation/informations_pratiques',
    '/offre/individuelle/offer-123/edition/informations_pratiques',
    '/offre/individuelle/offer-123/reservations',
    '/offre/individuelle/offer-123/creation/confirmation',
    '/offre/individuelle/offer-123/creation/recapitulatif',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes(
        [
          {
            path: '/offre/individuelle',
            children: routesIndividualOfferWizard,
          },
        ],
        path
      )
    ).not.toBeNull()
  })
})

describe('routesOnboardingIndividualOfferWizard', () => {
  it.each([
    '/onboarding/offre/individuelle/creation/description',
    '/onboarding/offre/individuelle/offer-123/creation/description',
    '/onboarding/offre/individuelle/offer-123/creation/pratiques',
    '/onboarding/offre/individuelle/offer-123/creation/localisation',
    '/onboarding/offre/individuelle/offer-123/creation/media',
    '/onboarding/offre/individuelle/offer-123/creation/tarifs',
    '/onboarding/offre/individuelle/offer-123/creation/informations_pratiques',
    '/onboarding/offre/individuelle/offer-123/creation/stocks',
    '/onboarding/offre/individuelle/offer-123/creation/horaires',
    '/onboarding/offre/individuelle/offer-123/creation/recapitulatif',
  ])('should have the path %s', (path) => {
    expect(
      matchRoutes(
        [
          {
            path: '/onboarding/offre/individuelle',
            children: routesOnboardingIndividualOfferWizard,
          },
        ],
        path
      )
    ).not.toBeNull()
  })
})
