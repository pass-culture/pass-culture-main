import { validateEmail, validatePhone, validateUrl } from '../validators'

describe('has fill fields with correct format', () => {
  it('should return undefined when phone number is valid or empty', () => {
    const fixPhoneNumber = '0111111111'
    const mobilePhoneNumber = '0611111111'
    const fixPhoneNumberWithPlus = '+33111111111'
    const mobilePhoneNumberWithPlus = '+33611111111'
    const emptyPhoneNumber = ''

    expect(validatePhone(fixPhoneNumber)).toBeUndefined()
    expect(validatePhone(mobilePhoneNumber)).toBeUndefined()
    expect(validatePhone(fixPhoneNumberWithPlus)).toBeUndefined()
    expect(validatePhone(mobilePhoneNumberWithPlus)).toBeUndefined()
    expect(validatePhone(emptyPhoneNumber)).toBeUndefined()
  })

  it('should return an error message when phone number is invalid', () => {
    const errorMessage = 'Votre numéro de téléphone n’est pas valide'

    const phoneNumberWithUnexpectedString = '+33111+11111'
    const tooLongPhoneNumber = '011111111111111'
    const tooShortPhoneNumber = '01'

    expect(validatePhone(phoneNumberWithUnexpectedString)).toStrictEqual(
      errorMessage
    )
    expect(validatePhone(tooLongPhoneNumber)).toStrictEqual(errorMessage)
    expect(validatePhone(tooShortPhoneNumber)).toStrictEqual(errorMessage)
  })

  it('should return undefined when eMail is valid or empty', async () => {
    const correctGmailEmail = 'jeans@gmail.com'
    const correctHotmailEmail = 'jeans@hotmail.fr'
    const correctYahooEmail = 'jeans@yahoo.com'
    const correctFreeEmail = 'jeans@free.com'
    const EmptyEmail = ''

    await expect(validateEmail(correctGmailEmail)).resolves.toBeUndefined()
    await expect(validateEmail(correctHotmailEmail)).resolves.toBeUndefined()
    await expect(validateEmail(correctYahooEmail)).resolves.toBeUndefined()
    await expect(validateEmail(correctFreeEmail)).resolves.toBeUndefined()
    await expect(validateEmail(EmptyEmail)).resolves.toBeUndefined()
  })
  // rename it and wrong and goo values
  it('should return an error message when Email is invalid', async () => {
    const errorMessage = 'Veuillez renseigner un email valide'

    const emailWithTwoArrowbases = 'jeans@@gmail.com'
    const emailWithNoDot = 'jeans@hotmailfr'
    const emailWithSpace = 'jeans free.com'
    const emailWithNoArrowbase = 'jeansfree.com'

    await expect(validateEmail(emailWithTwoArrowbases)).resolves.toStrictEqual(
      errorMessage
    )
    await expect(validateEmail(emailWithNoDot)).resolves.toStrictEqual(
      errorMessage
    )
    await expect(validateEmail(emailWithSpace)).resolves.toStrictEqual(
      errorMessage
    )
    await expect(validateEmail(emailWithNoArrowbase)).resolves.toStrictEqual(
      errorMessage
    )
  })

  it('should return undefined when Url is valid or empty', async () => {
    const httpUrl = 'http://someFakeUrl.com'
    const httpsUrl = 'https://someFakeUrl.com'
    const httpUrlWithUppercase = 'HTTP://www.someFakeUrl.com'
    const classicUrl = 'someFakeUrl.com'
    const classicUrlWithParameters = 'www.someFakeUrl.com?%20%23%42'
    const wwwClassicUrl = 'www.someFakeUrl.com'
    const emptyUrl = ''

    await expect(validateUrl(httpUrl)).resolves.toBeUndefined()
    await expect(validateUrl(httpsUrl)).resolves.toBeUndefined()
    await expect(validateUrl(httpUrlWithUppercase)).resolves.toBeUndefined()
    await expect(validateUrl(emptyUrl)).resolves.toBeUndefined()
    await expect(validateUrl(classicUrl)).resolves.toBeUndefined()
    await expect(validateUrl(classicUrlWithParameters)).resolves.toBeUndefined()
    await expect(validateUrl(wwwClassicUrl)).resolves.toBeUndefined()
  })

  it('should return an error message when Url is invalid', async () => {
    const errorMessage =
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'

    const stringText = 'some text'
    const urlWithoutSlash = 'http:someFakeUrl.com'
    const relativeUrl = '/someFakeUrl.com'

    await expect(validateUrl(stringText)).resolves.toStrictEqual(errorMessage)
    await expect(validateUrl(urlWithoutSlash)).resolves.toStrictEqual(
      errorMessage
    )
    await expect(validateUrl(relativeUrl)).resolves.toStrictEqual(errorMessage)
  })
})
