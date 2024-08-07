import { WithdrawalTypeEnum } from 'apiClient/v1'

import { getValidationSchema } from '../validationSchema'

const defaultAccessibility = {
  accessibility: {
    mental: false,
    audio: false,
    visual: false,
    motor: false,
    none: true,
  },
}

describe('getValidationSchema', () => {
  it('should validate withdrawalType correctly', async () => {
    const schema = getValidationSchema(['withdrawalType'])
    await expect(
      schema.validate({
        ...defaultAccessibility,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
      })
    ).resolves.toBeTruthy()

    await expect(schema.validate({ ...defaultAccessibility })).rejects.toThrow(
      'Veuillez sélectionner l’une de ces options'
    )
  })

  it('should validate withdrawalDelay correctly', async () => {
    const schema = getValidationSchema(['withdrawalDelay'])
    await expect(
      schema.validate({
        ...defaultAccessibility,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: 'Some delay',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultAccessibility,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: '',
      })
    ).rejects.toThrow('Vous devez choisir l’une des options ci-dessus')
  })

  it('should validate url correctly when isVenueVirtual is true', async () => {
    const schema = getValidationSchema([])
    await expect(
      schema.validate({
        ...defaultAccessibility,
        isVenueVirtual: true,
        url: 'https://example.com',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultAccessibility,
        isVenueVirtual: true,
        url: 'invalid-url',
      })
    ).rejects.toThrow(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    )
  })

  it('should validate bookingContact correctly', async () => {
    const schema = getValidationSchema(['bookingContact'])
    await expect(
      schema.validate({
        ...defaultAccessibility,
        bookingContact: 'valid@example.com',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultAccessibility,
        bookingContact: 'invalid-email',
      })
    ).rejects.toThrow(
      'Veuillez renseigner un email valide, exemple : mail@exemple.com'
    )

    await expect(
      schema.validate({
        ...defaultAccessibility,
        bookingContact: 'user@passculture.app',
      })
    ).rejects.toThrow('Ce mail doit vous appartenir')
  })

  it('should validate accessibility correctly', async () => {
    const schema = getValidationSchema([])
    await expect(
      schema.validate({
        accessibility: {
          mental: true,
          audio: false,
          visual: false,
          motor: false,
          none: false,
        },
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        accessibility: {
          mental: false,
          audio: false,
          visual: false,
          motor: false,
          none: false,
        },
      })
    ).rejects.toThrow(
      'Veuillez sélectionner au moins un critère d’accessibilité'
    )
  })

  it('should validate bookingEmail correctly when receiveNotificationEmails is true', async () => {
    const schema = getValidationSchema([])
    await expect(
      schema.validate({
        ...defaultAccessibility,
        receiveNotificationEmails: true,
        bookingEmail: 'valid@example.com',
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({
        ...defaultAccessibility,
        receiveNotificationEmails: true,
        bookingEmail: 'invalid-email',
      })
    ).rejects.toThrow(
      'Veuillez renseigner un email valide, exemple : mail@exemple.com'
    )
  })

  it('should validate externalTicketOfficeUrl correctly', async () => {
    const schema = getValidationSchema([])
    await expect(
      schema.validate({
        externalTicketOfficeUrl: 'https://example.com',
        ...defaultAccessibility,
      })
    ).resolves.toBeTruthy()

    await expect(
      schema.validate({ externalTicketOfficeUrl: 'invalid-url' })
    ).rejects.toThrow(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    )
  })
})
