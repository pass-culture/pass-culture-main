import { validateEmail, validatePhone, validateUrl } from "../validators"

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

    const errorMessage = 'Ce numéro de téléphone n’est pas valide merci de fournir un numéro de téléphone sans espaces'

    const phoneNumberWithSpaces = '01 11 11 11 11'
    const phoneNumberWithUnexpectedString = '+33111+11111'
    const tooLongPhoneNumber = '011111111111111'
    const tooShortPhoneNumber = '01'

    expect(validatePhone(phoneNumberWithSpaces)).toStrictEqual(errorMessage)
    expect(validatePhone(phoneNumberWithUnexpectedString)).toStrictEqual(errorMessage)
    expect(validatePhone(tooLongPhoneNumber)).toStrictEqual(errorMessage)
    expect(validatePhone(tooShortPhoneNumber)).toStrictEqual(errorMessage)
  })

  it('should return undefined when eMail is valid or empty', async () => {

    const correctGmailEmail = 'jeans@gmail.com'
    const correctHotmailEmail = 'jeans@hotmail.fr'
    const correctYahooEmail = 'jeans@yahoo.com'
    const correctFreeEmail = 'jeans@free.com'
    const EmptyEmail = ''

    expect(await validateEmail(correctGmailEmail)).toBeUndefined()
    expect(await validateEmail(correctHotmailEmail)).toBeUndefined()
    expect(await validateEmail(correctYahooEmail)).toBeUndefined()
    expect(await validateEmail(correctFreeEmail)).toBeUndefined()
    expect(await validateEmail(EmptyEmail)).toBeUndefined()
  })
  // rename it and wrong and goo values
  it('should return an error message when Email is invalid', async () => {

    const errorMessage = 'Votre email n’est pas valide'

    const emailWithTwoArrowbases = 'jeans@@gmail.com'
    const emailWithNoDot = 'jeans@hotmailfr'
    const emailWithSpace = 'jeans free.com'
    const emailWithNoArrowbase = 'jeansfree.com'

    expect(await validateEmail(emailWithTwoArrowbases)).toStrictEqual(errorMessage)
    expect(await validateEmail(emailWithNoDot)).toStrictEqual(errorMessage)
    expect(await validateEmail(emailWithSpace)).toStrictEqual(errorMessage)
    expect(await validateEmail(emailWithNoArrowbase)).toStrictEqual(errorMessage)
  })

  it('should return undefined when Url is valid or empty', async () => {

    const httpUrl = 'http://someFakeUrl.com'
    const httpsUrl = 'https://someFakeUrl.com'
    const emptyUrl = ''

    expect(await validateUrl(httpUrl)).toBeUndefined()
    expect(await validateUrl(httpsUrl)).toBeUndefined()
    expect(await validateUrl(emptyUrl)).toBeUndefined()
  })

  it('should return an error message when Url is invalid', async () => {

    const errorMessage = 'L’URL renseignée n’est pas valide'

    const stringText = 'some text'
    const urlWithoutSlash = 'http:someFakeUrl.com'
    const relativeUrl = '/someFakeUrl.com'

    expect(await validateUrl(stringText)).toStrictEqual(errorMessage)
    expect(await validateUrl(urlWithoutSlash)).toStrictEqual(errorMessage)
    expect(await validateUrl(relativeUrl)).toStrictEqual(errorMessage)
  })
})
