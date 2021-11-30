import * as yup from 'yup'

import { ADRESS_TYPE } from 'core/OfferEducational'

export const validationSchema = yup.object().shape({
  category: yup.string().required('Champ obligatoire'),
  subCategory: yup.string().required('Champ obligatoire'),
  title: yup.string().max(90).required('Champ obligatoire'),
  description: yup.string().max(1000),
  duration: yup.number(),
  offererId: yup.string().required('Champ obligatoire'),
  venueId: yup.string().required('Champ obligatoire'),
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
      otherAddress: yup.string(),
      venueId: yup.string(),
    })
    .required('Champ obligatoire'),
  participants: yup.array().of(yup.string()).min(1),
  visualDisabilityCompliant: yup.boolean(),
  mentalDisabilityCompliant: yup.boolean(),
  motorDisabilityCompliant: yup.boolean(),
  audioDisabilityCompliant: yup.boolean(),
  phone: yup.string().required('Champ obligatoire'),
  email: yup.string().email().required('Champ obligatoire'),
  notifications: yup.boolean(),
  notificationEmail: yup.string().when('notifications', {
    is: true,
    then: yup.string().required('Champ obligatoire').email(),
  }),
})
