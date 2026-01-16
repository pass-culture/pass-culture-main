import type { AccessibilityFormValues } from '@/commons/core/shared/types'

import type { DetailsFormValues } from '../types' // Assuming types are in a sibling file
import {
  eanSearchValidationSchema,
  getValidationSchema,
} from '../validationSchema'

describe('getValidationSchema', () => {
  const schema = getValidationSchema()

  const validDetailsFormValuesBase: Partial<DetailsFormValues> = {
    name: 'Valid Offer Name',
    categoryId: 'MUSIQUE',
    subcategoryId: 'CONCERT',
    venueId: 'venue-123',
    subcategoryConditionalFields: [],
    accessibility: {
      // Default for the new flow
      mental: false,
      audio: false,
      visual: false,
      motor: true,
      none: false,
    },
  }

  describe('accessibility validation', () => {
    it('should fail if accessibility object is missing', async () => {
      const data = { ...validDetailsFormValuesBase, accessibility: undefined }
      await expect(schema.validate(data)).rejects.toThrow(
        'Veuillez sélectionner au moins un critère d’accessibilité'
      )
    })

    it('should fail if no accessibility criteria is selected', async () => {
      const accessibility: AccessibilityFormValues = {
        mental: false,
        audio: false,
        visual: false,
        motor: false,
        none: false,
      }
      const data = { ...validDetailsFormValuesBase, accessibility }
      await expect(schema.validate(data)).rejects.toThrow(
        'Veuillez sélectionner au moins un critère d’accessibilité'
      )
    })

    it('should pass if at least one accessibility criterion is selected', async () => {
      const accessibility: AccessibilityFormValues = {
        mental: true,
        audio: false,
        visual: false,
        motor: false,
        none: false,
      }
      const data = { ...validDetailsFormValuesBase, accessibility }
      await expect(schema.validate(data)).resolves.toBeDefined()
    })

    it('should pass if "none" is selected', async () => {
      const accessibility: AccessibilityFormValues = {
        mental: false,
        audio: false,
        visual: false,
        motor: false,
        none: true,
      }
      const data = { ...validDetailsFormValuesBase, accessibility }
      await expect(schema.validate(data)).resolves.toBeDefined()
    })
  })
})

describe('eanSearchValidationSchema', () => {
  it('should pass with a valid EAN', async () => {
    await expect(
      eanSearchValidationSchema.validate({ eanSearch: '1234567890123' })
    ).resolves.toBeDefined()
  })

  it('should fail with an invalid EAN', async () => {
    await expect(
      eanSearchValidationSchema.validate({ eanSearch: 'invalid' })
    ).rejects.toThrow()
  })
})
