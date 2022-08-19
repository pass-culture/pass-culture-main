import { parseAndValidateFrenchPhoneNumber } from '../parseAndValidateFrenchPhoneNumber'

describe('french phone number without region code', () => {
  it('should parse french metropolitan phone number', () => {
    // Given
    const phoneNumber = '0601020304'

    // When
    const parsedPhoneNumber = parseAndValidateFrenchPhoneNumber(phoneNumber)

    // Then
    expect(parsedPhoneNumber.number).toEqual('+33601020304')
  })

  it('should reject too short phone number', () => {
    // Given
    const phoneNumber = '1'

    // When
    expect(() => parseAndValidateFrenchPhoneNumber(phoneNumber)).toThrowError(
      'Votre numéro de téléphone n’est pas valide'
    )
  })

  it('should reject too long phone number', () => {
    // Given
    const phoneNumber = '06010203041'

    // When
    expect(() => parseAndValidateFrenchPhoneNumber(phoneNumber)).toThrowError(
      'Votre numéro de téléphone n’est pas valide'
    )
  })

  it('should parse dom-tom phone number correctly', () => {
    // Given
    const guyanePhoneNumber = '0694120304'

    // When
    const parsedGuyanePhoneNumber =
      parseAndValidateFrenchPhoneNumber(guyanePhoneNumber)

    // Then
    expect(parsedGuyanePhoneNumber.number).toEqual('+594694120304')
  })
})

describe('french phone number with region code', () => {
  it('should parse french phone number with region code', () => {
    // Given
    const phoneNumber = '+33601020304'

    // When
    const parsedPhoneNumber = parseAndValidateFrenchPhoneNumber(phoneNumber)

    // Then
    expect(parsedPhoneNumber.number).toEqual('+33601020304')
  })
  it('should format french phone number with region code and starting 0', () => {
    // Given
    const phoneNumber = '+330601020304'

    // When
    const parsedPhoneNumber = parseAndValidateFrenchPhoneNumber(phoneNumber)

    // Then
    expect(parsedPhoneNumber.number).toEqual('+33601020304')
  })
  it('should reject non french phone number with region code', () => {
    // Given
    const phoneNumber = '+18601020304'

    // Then
    expect(() => parseAndValidateFrenchPhoneNumber(phoneNumber)).toThrowError(
      'Votre numéro de téléphone n’est pas valide'
    )
  })
  it('should reformat french phone number with region code and invalid prefix', () => {
    // Given
    const phoneNumberWithDomTomPrefix = '+33639020304'

    // When
    const parsedPhoneNumber = parseAndValidateFrenchPhoneNumber(
      phoneNumberWithDomTomPrefix
    )

    // Then
    expect(parsedPhoneNumber.number).toEqual('+262639020304')
  })
})

describe('dom-tom phone number with region code', () => {
  it('should parse dom-tom phone number with region code', () => {
    // Given
    const phoneNumber = '+262639020304'

    // When
    const parsedPhoneNumber = parseAndValidateFrenchPhoneNumber(phoneNumber)

    // Then
    expect(parsedPhoneNumber.number).toEqual('+262639020304')
  })
  it('should reject non dom-tom phone number with region code', () => {
    // Given
    const invalidPhoneNumber = '+180601020304'

    // Then
    expect(() =>
      parseAndValidateFrenchPhoneNumber(invalidPhoneNumber)
    ).toThrowError('Votre numéro de téléphone n’est pas valide')
  })
  it('should reject  dom-tom phone number with region code and invalid prefix', () => {
    // Given
    const phoneNumberWithInvalidPrefix = '+262601020304'

    // Then
    expect(() =>
      parseAndValidateFrenchPhoneNumber(phoneNumberWithInvalidPrefix)
    ).toThrowError('Votre numéro de téléphone n’est pas valide')
  })
})
