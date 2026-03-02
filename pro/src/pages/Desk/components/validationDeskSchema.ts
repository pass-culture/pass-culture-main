import { yup } from '@/commons/utils/yup'

const TOKEN_MAX_LENGTH = 6
const VALID_TOKEN_SYNTAX = /^[A-Z0-9]+$/

export const validationDeskSchema = yup.object({
  token: yup
    .string()
    .required('Saisissez une contremarque')
    .length(TOKEN_MAX_LENGTH, 'La contremarque doit contenir 6 caractères')
    .matches(VALID_TOKEN_SYNTAX, 'Caractères valides : de A à Z et de 0 à 9'),
})
