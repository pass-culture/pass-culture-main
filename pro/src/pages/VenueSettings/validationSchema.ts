import * as yup from 'yup'

export const getValidationSchema = (isVenueVirtual: boolean) =>
  yup.object().shape({
    addressAutocomplete: isVenueVirtual
      ? yup.string()
      : yup
          .string()
          .required('Veuillez sélectionner une adresse parmi les suggestions'),
    bookingEmail: isVenueVirtual
      ? yup.string()
      : yup
          .string()
          .email(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )
          .required('Veuillez renseigner une adresse email'),
    name: yup
      .string()
      .required(`Veuillez renseigner la raison sociale de votre lieu`),
    venueType: yup
      .string()
      .required('Veuillez sélectionner une activité principale'),
  })
