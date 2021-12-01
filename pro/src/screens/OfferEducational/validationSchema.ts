import * as yup from 'yup'

import { ADRESS_TYPE } from 'core/OfferEducational'

export const validationSchema = yup.object().shape({
  category: yup.string().required('Veuillez selectionner une catégorie'),
  subCategory: yup
    .string()
    .required('Veuillez selectionner une sous catégorie'),
  title: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
  duration: yup
    .string()
    .matches(
      /[0-9]{1,3}:[0-5][0-9]/,
      'Veuillez renseigner une durée en heures au format hh:mm. exemple: 12:30'
    ),
  offererId: yup.string().required('Veuillez selectionner une structure'),
  venueId: yup.string().required('Veuillez selectionner un lieu'),
  eventAddress: yup
    .object()
    .shape({
      addressType: yup
        .string()
        .oneOf([
          ADRESS_TYPE.OFFERER_VENUE,
          ADRESS_TYPE.OTHER,
          ADRESS_TYPE.SCHOOL,
        ])
        .required('Champ obligatoire'),
      otherAddress: yup.string().when('addressType', {
        is: ADRESS_TYPE.OTHER,
        then: yup.string().required('Veuillez renseigner une adresse'),
      }),
      venueId: yup.string().when('addressType', {
        is: ADRESS_TYPE.OFFERER_VENUE,
        then: yup.string().required('Veuillez selectionner un lieu'),
      }),
    })
    .required('Champ obligatoire'),
  participants: yup
    .array()
    .of(yup.string())
    .min(1, 'Veuillez selectionner au moins un publique cible'),
  accessibility: yup
    .array()
    .of(yup.string())
    .min(1, 'Veuillez selectionner au moins un critère d’accessibilité'),
  phone: yup
    .string()
    .required('Veuillez renseigner un numéro de téléphone de contact'),
  email: yup
    .string()
    .required('Veuillez renseigner une adresse email de contact')
    .email('L’email renseigné n’est pas valide. exemple: mon.email@gmail.com'),
  notifications: yup.boolean(),
  notificationEmail: yup.string().when('notifications', {
    is: true,
    then: yup
      .string()
      .required('Veuillez renseigner un email pour vos notifications')
      .email(
        'L’email renseigné n’est pas valide. exemple: mon.email@gmail.com'
      ),
  }),
})
