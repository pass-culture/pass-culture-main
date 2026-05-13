import * as yup from 'yup'

import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { emailSchema } from '@/commons/utils/isValidEmail'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

import type { CollectiveDataFormValues } from './type'

export const validationSchema = yup.object<CollectiveDataFormValues>().shape({
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
    .mixed<ActivityOpenToPublicType | ActivityNotOpenToPublicType>()
    .nullable()
    .required('Veuillez renseigner ce champ'),
})
