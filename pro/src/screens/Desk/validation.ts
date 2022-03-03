import { IErrorMessage, MESSAGE_VARIANT } from './types'

const TOKEN_MAX_LENGTH = 6
const VALID_TOKEN_SYNTAX = /[^a-z0-9]/i

export const validateToken = (token: string): IErrorMessage | false => {
  const validationRules = [
    {
      check: (token: string) => token === '',
      hasError: false,
      message: 'Saisissez une contremarque',
    },
    {
      check: (token: string) => token.match(VALID_TOKEN_SYNTAX) !== null,
      hasError: true,
      message: 'Caractères valides : de A à Z et de 0 à 9',
    },
    {
      check: (token: string) => token.length < TOKEN_MAX_LENGTH,
      hasError: false,
      message: `Caractères restants : ${
        TOKEN_MAX_LENGTH - token.length
      }/${TOKEN_MAX_LENGTH}`,
    },
    {
      check: (token: string) => token.length > TOKEN_MAX_LENGTH,
      hasError: true,
      message: `La contremarque ne peut pas faire plus de ${TOKEN_MAX_LENGTH} caractères`,
    },
  ]

  const error = validationRules.find(rule => rule.check(token))
  if (error) {
    return {
      message: error.message,
      variant: error.hasError ? MESSAGE_VARIANT.ERROR : MESSAGE_VARIANT.DEFAULT,
    }
  }
  return false
}
