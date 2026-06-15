import type { ActivityOpenToPublic } from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { yup } from '@/commons/utils/yup'

import { venueSettingsValidationSchema } from '../schema'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'

describe('VenueSettingsValidationSchema', () => {
  const baseContext: VenueSettingsFormContext = {
    isCaledonian: false,
    withSiret: true,
    siren: '123456789',
    isOpenToPublic: 'true',
  }

  const baseFormValues: VenueSettingsFormValues = {
    comment: 'comment',
    name: 'Venue Name',
    publicName: 'Venue Public Name',
    siret: '12345678901234',
    venueSiret: 12345678901234,
    withdrawalDetails:
      "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    manuallySetAddress: false,
    addressAutocomplete: '123 Rue Principale, Ville Exemple',
    banId: '12345',
    city: 'Ville Exemple',
    latitude: '48.8566',
    longitude: '2.3522',
    coords: '48.8566, 2.3522',
    postalCode: '75001',
    inseeCode: '75111',
    'search-addressAutocomplete': '123 Rue Principale, Ville Exemple',
    street: '123 Rue Principale',
    isOpenToPublic: 'true',
    activity: 'ART_GALLERY' as ActivityOpenToPublic,
    accessibility: {
      visual: true,
      mental: false,
      audio: false,
      motor: false,
      none: false,
    },
    isAccessibilityAppliedOnAllOffers: false,
  }

  interface Case {
    description: string
    formValues: VenueSettingsFormValues
    context: VenueSettingsFormContext
    expectedErrors: string[]
  }

  const cases: Case[] = [
    {
      description: 'invalid - addressAutocomplete required',
      formValues: {
        ...baseFormValues,
        addressAutocomplete: '',
        manuallySetAddress: false,
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [
        'Veuillez sélectionner une adresse parmi les suggestions',
      ],
    },
    {
      description: 'valid - addressAutocomplete',
      formValues: {
        ...baseFormValues,
        addressAutocomplete: '',
        manuallySetAddress: true,
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [],
    },
    {
      description: 'invalid - coords required',
      formValues: {
        ...baseFormValues,
        coords: '',
        manuallySetAddress: true,
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [
        'Veuillez renseigner les coordonnées GPS',
        'Veuillez respecter le format attendu',
      ],
    },
    {
      description: 'invalid - activity required',
      formValues: {
        ...baseFormValues,
        activity: null,
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [
        'Veuillez sélectionner une activité parmi les suggestions',
      ],
    },
  ]

  cases.forEach(({ description, formValues, context, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const collected: string[] = []
      try {
        await venueSettingsValidationSchema.validate(formValues, {
          abortEarly: false,
          context: {
            ...context,
          },
        })
      } catch (error) {
        assertOrFrontendError(
          error instanceof yup.ValidationError,
          'Expected yup.ValidationError'
        )

        collected.push(...error.errors)
      }

      expect(collected).toEqual(expectedErrors)
    })
  })
})
