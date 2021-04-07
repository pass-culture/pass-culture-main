import strings from '../strings'
import validateEmailField from '../validateEmailField'

describe('src | components | forms | validators | validateEmailField', () => {
  it.each`
    email
    ${''}
    ${'     '}
    ${'example@example'}
  `('expect to return default error - not a valid email \t= $email', ({ email }) => {
    const expected = strings.EMAIL_ERROR_MESSAGE
    expect(validateEmailField(email)).toStrictEqual(expected)
  })

  it.each`
    email
    ${'example@example.com'}
    ${'example+example@example.fr'}
    ${'example.example@example.com'}
    ${'exa.mple@example.example.com'}
    ${'example-example@example.com'}
  `('expect to return undefined - valid email \t= $email', ({ email }) => {
    const expected = undefined
    expect(validateEmailField(email)).toStrictEqual(expected)
  })
})
