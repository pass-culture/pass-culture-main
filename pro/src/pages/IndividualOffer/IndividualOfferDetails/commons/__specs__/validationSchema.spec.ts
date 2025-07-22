import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { AccessibilityFormValues } from 'commons/core/shared/types'
import { subcategoryFactory } from 'commons/utils/factories/individualApiFactories'

import { DetailsFormValues } from '../types' // Assuming types are in a sibling file
import {
  eanSearchValidationSchema,
  getValidationSchema,
  getValidationSchemaForNewOfferCreationFlow,
} from '../validationSchema'

describe('getValidationSchema', () => {
  const isOfferDigital = false
  const schema = getValidationSchema(isOfferDigital)

  const validDetailsFormValuesBase: Partial<DetailsFormValues> = {
    name: 'Valid Offer Name',
    categoryId: 'MUSIQUE',
    subcategoryId: 'CONCERT',
    venueId: 'venue-123',
    subcategoryConditionalFields: [],
  }

  it('should pass for a minimal valid physical offer', async () => {
    const schema = getValidationSchema(isOfferDigital)
    const data = {
      ...validDetailsFormValuesBase,
    }
    await expect(schema.validate(data)).resolves.toBeDefined()
  })

  it('should fail if name is missing', async () => {
    const schema = getValidationSchema(isOfferDigital)
    const data = { ...validDetailsFormValuesBase, name: '' }
    await expect(schema.validate(data)).rejects.toThrow(
      'Veuillez renseigner un titre'
    )
  })

  it('should fail if name is longer than 90 characters', async () => {
    const schema = getValidationSchema(isOfferDigital)
    const data = { ...validDetailsFormValuesBase, name: 'a'.repeat(91) }
    await expect(schema.validate(data)).rejects.toThrow(
      'name must be at most 90 characters'
    )
  })

  it('should require showType and showSubType when specified in conditional fields', async () => {
    const dataWithoutShowType = {
      ...validDetailsFormValuesBase,
      subcategoryConditionalFields: ['showType'],
      showSubType: 'POP',
    }
    await expect(schema.validate(dataWithoutShowType)).rejects.toThrow(
      'Veuillez sélectionner un type de spectacle'
    )

    const dataWithoutShowSubType = {
      ...validDetailsFormValuesBase,
      subcategoryConditionalFields: ['showType'],
      showType: 'CONCERT',
    }
    await expect(schema.validate(dataWithoutShowSubType)).rejects.toThrow(
      'Veuillez sélectionner un sous-type de spectacle'
    )

    const validData = { ...dataWithoutShowSubType, showSubType: 'POP' }
    await expect(schema.validate(validData)).resolves.toBeDefined()
  })

  it('should require a valid URL for a digital offer', async () => {
    const isOfferDigital = true
    const schema = getValidationSchema(isOfferDigital)

    const data = { ...validDetailsFormValuesBase }
    await expect(schema.validate(data)).rejects.toThrow(
      'Veuillez renseigner une URL valide'
    )

    const dataWithInvalidUrl = { ...data, url: 'not-a-url' }
    await expect(schema.validate(dataWithInvalidUrl)).rejects.toThrow(
      'Veuillez renseigner une URL valide'
    )

    const dataWithValidUrl = { ...data, url: 'https://example.com' }
    await expect(schema.validate(dataWithValidUrl)).resolves.toBeDefined()
  })

  it('should NOT require a URL for a physical offer', async () => {
    const isOfferDigital = false
    const schema = getValidationSchema(isOfferDigital)

    const data = { ...validDetailsFormValuesBase, url: null }
    await expect(schema.validate(data)).resolves.toBeDefined()
  })

  describe('EAN validation', () => {
    const schema = getValidationSchema(isOfferDigital)

    it('should accept a valid 13-digit EAN', async () => {
      const data = { ...validDetailsFormValuesBase, ean: '1234567890123' }
      await expect(schema.validate(data)).resolves.toBeDefined()
    })

    it('should fail if EAN is not 13 digits', async () => {
      const data = { ...validDetailsFormValuesBase, ean: '12345' }
      await expect(schema.validate(data)).rejects.toThrow(
        "L'EAN doit être composé de 13 chiffres."
      )
    })

    it('should fail if EAN contains non-digit characters', async () => {
      const data = { ...validDetailsFormValuesBase, ean: '123456789012a' }
      await expect(schema.validate(data)).rejects.toThrow(
        "L'EAN doit être composé de 13 chiffres"
      )
    })
  })

  describe('conditional fields (duration, showType, etc.)', () => {
    const schema = getValidationSchema(isOfferDigital)

    it('should validate HH:MM format for durationMinutes', async () => {
      const dataWithInvalidDuration = {
        ...validDetailsFormValuesBase,
        subcategoryConditionalFields: ['durationMinutes'],
        durationMinutes: '99:99',
      }
      await expect(schema.validate(dataWithInvalidDuration)).rejects.toThrow(
        'Veuillez entrer une durée sous la forme HH:MM'
      )

      const dataWithValidDuration = {
        ...validDetailsFormValuesBase,
        subcategoryConditionalFields: ['durationMinutes'],
        durationMinutes: '01:30',
      }
      await expect(
        schema.validate(dataWithValidDuration)
      ).resolves.toBeDefined()
    })
  })
})

describe('getValidationSchemaForNewOfferCreationFlow', () => {
  const subcategories = [
    subcategoryFactory({
      id: 'ONLINE_SUBCATEGORY',
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
    }),
    subcategoryFactory({
      id: 'OFFLINE_SUBCATEGORY',
      onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
    }),
    subcategoryFactory({
      id: 'ONLINE_OR_OFFLINE_SUBCATEGORY',
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
    }),
  ]
  const schema = getValidationSchemaForNewOfferCreationFlow(subcategories)

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

  it('should require a valid URL when the selected subcategory is or may be an event', async () => {
    const data = {
      ...validDetailsFormValuesBase,
      subcategoryId: 'ONLINE_SUBCATEGORY',
    }
    await expect(schema.validate(data)).rejects.toThrow(
      'Veuillez renseigner une URL valide'
    )

    const dataWithInvalidUrl = {
      ...data,
      url: 'not-a-url',
    }
    await expect(schema.validate(dataWithInvalidUrl)).rejects.toThrow(
      'Veuillez renseigner une URL valide'
    )

    const dataWithValidUrl = { ...data, url: 'https://example.com' }
    await expect(schema.validate(dataWithValidUrl)).resolves.toBeDefined()
  })

  it('should NOT require a URL when the selected subcategory may be offline', async () => {
    const dataWithOfflineSubcategory = {
      ...validDetailsFormValuesBase,
      subcategoryId: 'OFFLINE_SUBCATEGORY',
    }
    await expect(
      schema.validate(dataWithOfflineSubcategory)
    ).resolves.toBeDefined()

    const dataWithOnlineOrOfflineSubcategory = {
      ...validDetailsFormValuesBase,
      subcategoryId: 'ONLINE_OR_OFFLINE_SUBCATEGORY',
    }
    await expect(
      schema.validate(dataWithOnlineOrOfflineSubcategory)
    ).resolves.toBeDefined()
  })

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
