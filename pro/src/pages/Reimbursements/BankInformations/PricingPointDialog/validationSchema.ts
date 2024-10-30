import * as yup from 'yup'

export const getValidationSchema = ({
  isOfferAddressEnabled = false,
}: {
  isOfferAddressEnabled?: boolean
}) =>
  yup.object().shape({
    pricingPointId: yup
      .string()
      .required(
        isOfferAddressEnabled
          ? 'Veuillez sélectionner une structure avec SIRET'
          : 'Veuillez sélectionner un lieu avec SIRET'
      ),
  })
