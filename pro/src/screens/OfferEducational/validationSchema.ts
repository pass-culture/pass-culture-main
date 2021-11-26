import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  category: yup.string().required('Champ obligatoire'),
  subCategory: yup.string().required('Champ obligatoire'),
  title: yup.string().max(90).required('Champ obligatoire'),
  description: yup.string().max(1000),
  duration: yup.number(),
  offererId: yup.string().required('Champ obligatoire'),
  venueId: yup.string().required('Champ obligatoire'),
  offerVenueId: yup.string().required('Champ obligatoire'),
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
