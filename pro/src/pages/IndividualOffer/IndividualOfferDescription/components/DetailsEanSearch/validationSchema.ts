import { yup } from '@/commons/utils/yup'

const eanValidation = yup
  .string()
  .matches(/^\d*$/, "L'EAN doit être composé de 13 chiffres")
  .test({
    message: "L'EAN doit être composé de 13 chiffres.",
    test: (ean) => !ean || ean.length === 13,
  })

export const generateEanSearchValidationSchema = (required: boolean) => {
  return yup.object().shape({
    eanSearch: required
      ? eanValidation.required(
          'Les offres de type CD doivent être liées à un produit.'
        )
      : eanValidation,
  })
}

export type EanSearchForm = yup.InferType<
  ReturnType<typeof generateEanSearchValidationSchema>
>
