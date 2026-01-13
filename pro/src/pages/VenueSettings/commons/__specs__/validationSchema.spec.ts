import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { yup } from '@/commons/utils/yup'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import { venueSettingsValidationSchema } from '../validationSchema'

describe('VenueSettingsValidationSchema', () => {
  const baseContext: VenueSettingsFormContext = {
    isCaledonian: false,
    withSiret: true,
    siren: '123456789',
    isVenueVirtual: false,
  }

  const baseFormValues: VenueSettingsFormValues = {
    bookingEmail: 'contact@lieuexemple.com',
    comment: 'comment',
    name: 'Venue Name',
    publicName: 'Venue Public Name',
    siret: '12345678901234',
    venueSiret: 12345678901234,
    venueType: 'Théâtre',
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
        isVenueVirtual: false,
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
        manuallySetAddress: false,
      },
      context: {
        ...baseContext,
        isVenueVirtual: true,
      },
      expectedErrors: [],
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
        isVenueVirtual: false,
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
      description: 'invalid - bookingEmail format invalid',
      formValues: {
        ...baseFormValues,
        bookingEmail: 'email1@example.com email2@example.com',
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [
        'Veuillez renseigner un email valide, exemple : mail@exemple.com',
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
