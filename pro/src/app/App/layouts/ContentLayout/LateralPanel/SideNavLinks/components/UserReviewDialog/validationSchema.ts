import * as yup from 'yup'

import type { UserReviewDialogFormValues } from './UserReviewDialog'

export const validationSchema = yup.object<UserReviewDialogFormValues>().shape({
  userSatisfaction: yup.string().required(),
  userComment: yup
    .string()
    .max(500)
    .required('Veuillez renseigner un commentaire'),
})
