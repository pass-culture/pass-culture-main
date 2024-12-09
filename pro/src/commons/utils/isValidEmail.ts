const INVALID_EMAIL_MESSAGE =
  'Veuillez renseigner un email valide, exemple : mail@exemple.com'

export function isValidEmail(email: string) {
  const re = new RegExp(
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  )
  return re.test(email.trim())
}

//  Yup shema to be used instead of yup.email
//  yup.email uses the official HTML regex that is too permissive for our needs
//  https://html.spec.whatwg.org/multipage/input.html#valid-e-mail-address
export const emailSchema = {
  name: 'is-valid-email',
  message: INVALID_EMAIL_MESSAGE,
  test: (email?: string | null) => !email || isValidEmail(email),
}
