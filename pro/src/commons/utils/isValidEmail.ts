const INVALID_EMAIL_MESSAGE =
  'Veuillez renseigner un email valide, exemple : mail@exemple.com'

export const EMAIL_REGEXP =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9-]{1,61})*\.[a-zA-Z]{2,}$/

export function isValidEmail(email: string): boolean {
  // Regex officielle du standard WHATWG (HTML5)
  return EMAIL_REGEXP.test(email.trim())
}

//  Yup shema to be used instead of yup.email
//  yup.email uses the official HTML regex that is too permissive for our needs
//  https://html.spec.whatwg.org/multipage/input.html#valid-e-mail-address
export const emailSchema = {
  name: 'is-valid-email',
  message: INVALID_EMAIL_MESSAGE,
  test: (email?: string | null) => !email || isValidEmail(email),
}
