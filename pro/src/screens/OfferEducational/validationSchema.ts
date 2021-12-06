import * as yup from 'yup'

import { ADRESS_TYPE } from 'core/OfferEducational'

export const validationSchema = yup.object().shape({
  category: yup.string().required('Veuillez sélectionner une catégorie'),
  subCategory: yup
    .string()
    .required('Veuillez sélectionner une sous-catégorie'),
  title: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
  duration: yup
    .string()
    .matches(
      /[0-9]{1,2}:[0-5][0-9]/,
      'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
    ),
  offererId: yup.string().required('Veuillez sélectionner une structure'),
  venueId: yup.string().required('Veuillez sélectionner un lieu'),
  eventAddress: yup.object().shape({
    addressType: yup
      .string()
      .oneOf([
        ADRESS_TYPE.OFFERER_VENUE,
        ADRESS_TYPE.OTHER,
        ADRESS_TYPE.SCHOOL,
      ]),
    otherAddress: yup.string().when('addressType', {
      is: ADRESS_TYPE.OTHER,
      then: yup.string().required('Veuillez renseigner une adresse'),
    }),
    venueId: yup.string().when('addressType', {
      is: ADRESS_TYPE.OFFERER_VENUE,
      then: yup.string().required('Veuillez sélectionner un lieu'),
    }),
  }),
  participants: yup.object().test({
    name: 'one-true',
    message: 'Veuillez sélectionner au moins un niveau scolaire',
    test: (values: Record<string, boolean>): boolean =>
      Object.values(values).includes(true),
  }),
  accessibility: yup
    .object()
    .test({
      name: 'one-true',
      message: 'Veuillez sélectionner au moins un critère d’accessibilité',
      test: (values: Record<string, boolean>): boolean =>
        Object.values(values).includes(true),
    })
    .shape({
      mental: yup.boolean(),
      audio: yup.boolean(),
      visual: yup.boolean(),
      motor: yup.boolean(),
      none: yup.boolean(),
    }),
  phone: yup.string().required('Veuillez renseigner un numéro de téléphone'),
  email: yup
    .string()
    .required('Veuillez renseigner une adresse email')
    .email('L’email renseigné n’est pas valide. Exemple : email@gmail.com'),
  notifications: yup.boolean(),
  notificationEmail: yup.string().when('notifications', {
    is: true,
    then: yup
      .string()
      .required('Veuillez renseigner une adresse email')
      .email('L’email renseigné n’est pas valide. Exemple : email@gmail.com'),
  }),
})
