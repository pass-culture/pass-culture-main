import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import type { VenueEditionFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

describe('VenueEditionForm validationSchema', () => {
  const defaultValues: VenueEditionFormValues = {
    accessibility: {
      audio: true,
      mental: true,
      motor: true,
      none: false,
      visual: true,
    },
    isAccessibilityAppliedOnAllOffers: false,
    isOpenToPublic: 'true',
    openingHours: null,
    description: 'description',
    activity: 'ART_GALLERY',
  }

  const cases: {
    description: string
    formValues: VenueEditionFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for immediate booking and publication',
      formValues: defaultValues,
      expectedErrors: [],
    },
    {
      description: 'invalid form for an email with the wrong format',
      formValues: { ...defaultValues, email: 'test' },
      expectedErrors: [
        'Veuillez renseigner un email valide, exemple : mail@exemple.com',
      ],
    },
    {
      description: 'invalid form for a phone number with the wrong format',
      formValues: { ...defaultValues, phoneNumber: '1212' },
      expectedErrors: [
        'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
      ],
    },
    {
      description: 'invalid form for a website with the wrong format',
      formValues: { ...defaultValues, webSite: '1212' },
      expectedErrors: [
        'Veuillez renseigner une URL valide. Ex : https://exemple.com',
      ],
    },
    {
      description:
        'invalid form for missing accessibility information when the venue is open to public',
      formValues: {
        ...defaultValues,
        isOpenToPublic: 'true',
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: false,
          visual: false,
        },
      },
      expectedErrors: [
        'Veuillez sélectionner au moins un critère d’accessibilité',
      ],
    },
    {
      description:
        'invalid form for missing ending span in opening hours timespans',
      formValues: {
        ...defaultValues,
        openingHours: { MONDAY: [['12:12', '']] },
      },
      expectedErrors: ['Heure obligatoire'],
    },
    {
      description:
        'invalid form for missing beginning span in opening hours timespans',
      formValues: {
        ...defaultValues,
        openingHours: { MONDAY: [['', '12:12']] },
      },
      expectedErrors: ['Heure obligatoire'],
    },
    {
      description: 'invalid form for an end span before the start span',
      formValues: {
        ...defaultValues,
        openingHours: { MONDAY: [['13:13', '12:12']] },
      },
      expectedErrors: ['Plage horaire incohérente'],
    },
    {
      description: 'invalid form for overlapping timespans',
      formValues: {
        ...defaultValues,
        openingHours: {
          MONDAY: [
            ['12:12', '15:15'],
            ['14:14', '16:16'],
          ],
        },
      },
      expectedErrors: ['Plages horaires incompatibles'],
    },
    {
      description: 'valid form for non open to public and empty openingHours',
      formValues: {
        ...defaultValues,
        isOpenToPublic: 'false',
        activity: 'PRESS',
        openingHours: {
          MONDAY: null,
        },
      },
      expectedErrors: [],
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(getValidationSchema(), {
        ...formValues,
        culturalDomains: ['test'],
      })
      expect(errors).toEqual(expectedErrors)
    })
  })

  it('should require activity when feature flag is enabled and venue is open to public', async () => {
    const errors = await getYupValidationSchemaErrors(getValidationSchema(), {
      ...defaultValues,
      activity: null,
      culturalDomains: ['string'],
    })

    expect(errors).toEqual(['Veuillez renseigner ce champ'])
  })

  it('should require domains array', async () => {
    const errors = await getYupValidationSchemaErrors(getValidationSchema(), {
      ...defaultValues,
      isOpenToPublic: 'false',
      activity: 'PRESS',
      culturalDomains: null,
    })

    expect(errors).toEqual([
      'Veuillez sélectionner un ou plusieurs domaines d’activité',
    ])
  })

  it('should require domains values', async () => {
    const errors = await getYupValidationSchemaErrors(getValidationSchema(), {
      ...defaultValues,
      isOpenToPublic: 'false',
      activity: 'PRESS',
      culturalDomains: [],
    })

    expect(errors).toEqual([
      'Veuillez sélectionner un ou plusieurs domaines d’activité',
    ])
  })
})
