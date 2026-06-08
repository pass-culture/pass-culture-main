import * as yup from 'yup'

import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1/new'
import { ActivityNotOpenToPublicMap } from '@/commons/mappings/ActivityNotOpenToPublic'
import { ActivityOpenToPublicMap } from '@/commons/mappings/ActivityOpenToPublic'
import { getMapKeys } from '@/commons/mappings/helpers'

const activityTypeValuesOpenToPublic = getMapKeys(
  ActivityOpenToPublicMap
) as ActivityOpenToPublic[]
const activityTypeValuesNotOpenToPublic = getMapKeys(
  ActivityNotOpenToPublicMap
) as ActivityNotOpenToPublic[]

export const activityValidator = (notOpenToPublic: boolean) =>
  notOpenToPublic
    ? yup
        .mixed<ActivityNotOpenToPublic>()
        .oneOf(activityTypeValuesNotOpenToPublic, 'Activité non valide')
    : yup
        .mixed<ActivityOpenToPublic>()
        .oneOf(activityTypeValuesOpenToPublic, 'Activité non valide')
