import { WithdrawalTypeEnum } from 'apiClient/v1'

import { getValidationSchema } from '../validationSchema'

const defaultLocation = {
  locationLabel: 'label',
  offerLocation: 'location',
  addressAutocomplete: 'autocomplete',
  street: 'street',
  postalCode: '93160',
  city: 'city',
}
const defaultAccessibility = {
  accessibility: {
    mental: false,
    audio: false,
    visual: false,
    motor: false,
    none: true,
  },
}
const defaultValue = {
  ...defaultAccessibility,
  ...defaultLocation,
}

describe('getValidationSchema', () => {
  it('should validate withdrawalType correctly', async () => {
    const schema = getValidationSchema({ subcategories: ['withdrawalType'] })
    await expect(
      schema.validate({
        ...defaultValue,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
      })
    ).resolves.toBeTruthy()

    await expect(schema.validate({ ...defaultValue })).rejects.toThrow(
      'Veuillez sélectionner l’une de ces options'
    )
  })

  it('should validate withdrawalDelay correctly', async () => {
    const schema = getValidationSchema({ subcategories: ['withdrawalDelay'] })
    await expect(
      schema.validate({
        ...defaultValue,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: 'Some delay',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultValue,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: '',
      })
    ).rejects.toThrow('Vous devez choisir l’une des options ci-dessus')
  })

  it('should validate bookingContact correctly', async () => {
    const schema = getValidationSchema({ subcategories: ['bookingContact'] })
    await expect(
      schema.validate({
        ...defaultValue,
        bookingContact: 'valid@example.com',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultValue,
        bookingContact: 'invalid-email',
      })
    ).rejects.toThrow(
      'Veuillez renseigner un email valide, exemple : mail@exemple.com'
    )

    await expect(
      schema.validate({
        ...defaultValue,
        bookingContact: 'user@passculture.app',
      })
    ).rejects.toThrow('Ce mail doit vous appartenir')
  })

  it('should validate accessibility correctly', async () => {
    const schema = getValidationSchema({ subcategories: [] })
    await expect(
      schema.validate({
        ...defaultValue,
        accessibility: {
          mental: true,
          audio: false,
          visual: false,
          motor: false,
          none: false,
        },
        ...defaultLocation,
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultValue,
        accessibility: {
          mental: false,
          audio: false,
          visual: false,
          motor: false,
          none: false,
        },
        ...defaultLocation,
      })
    ).rejects.toThrow(
      'Veuillez sélectionner au moins un critère d’accessibilité'
    )
  })

  it('should validate bookingEmail correctly when receiveNotificationEmails is true', async () => {
    const schema = getValidationSchema({ subcategories: [] })
    await expect(
      schema.validate({
        ...defaultValue,
        receiveNotificationEmails: true,
        bookingEmail: 'valid@example.com',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultValue,
        receiveNotificationEmails: true,
        bookingEmail: 'invalid-email',
      })
    ).rejects.toThrow(
      'Veuillez renseigner un email valide, exemple : mail@exemple.com'
    )
  })

  it('should validate externalTicketOfficeUrl correctly', async () => {
    const schema = getValidationSchema({ subcategories: [] })
    await expect(
      schema.validate({
        ...defaultValue,
        externalTicketOfficeUrl: 'https://example.com',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultValue,
        externalTicketOfficeUrl: 'invalid-url',
      })
    ).rejects.toThrow(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    )
  })

  it('should validate address correctly', async () => {
    const schema = getValidationSchema({ subcategories: [] })
    await expect(schema.validate(defaultValue)).resolves.toBeTruthy()

    const valuesWithoutSelectedOfferLocation = {
      ...defaultLocation,
      ...defaultAccessibility,
      offerLocation: '',
    }
    await expect(
      schema.validate(valuesWithoutSelectedOfferLocation)
    ).rejects.toThrow('Veuillez sélectionner un choix')

    const virtualSchema = getValidationSchema({
      subcategories: [],
      isDigitalOffer: true,
    })
    await expect(
      virtualSchema.validate({
        ...defaultLocation,
        ...defaultAccessibility,
      })
    ).resolves.toBeTruthy()
  })
})
