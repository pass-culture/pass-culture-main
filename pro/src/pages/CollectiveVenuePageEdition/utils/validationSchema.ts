import * as yup from 'yup'

import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import { emailSchema } from '@/commons/utils/isValidEmail'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

import type { CollectiveVenuePageValues } from './type'

export const validationSchema = yup.object<CollectiveVenuePageValues>().shape({
  collectiveDescription: yup.string(),
  collectiveStudents: yup.array(),
  collectiveWebsite: yup
    .string()
    .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
  collectivePhone: phoneNumberSchema(),
  collectiveEmail: yup.string().test(emailSchema),
  collectiveDomains: yup.array(),
  collectiveLegalStatus: yup.string(),
  collectiveInterventionArea: yup.array(),
  activity: yup
    .mixed<ActivityOpenToPublic | ActivityNotOpenToPublic>()
    .nullable()
    .required('Veuillez renseigner ce champ'),
})
