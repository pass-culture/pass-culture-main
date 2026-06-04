import type { ActivityNotOpenToPublicType } from 'commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from 'commons/mappings/ActivityOpenToPublic'
import { getActivities } from 'commons/mappings/mappings'
import * as yup from 'yup'

import { objectKeys } from '../object'

const activityTypeValuesOpenToPublic = objectKeys(
  getActivities('OPEN_TO_PUBLIC')
)
const activityTypeValuesNotOpenToPublic = objectKeys(
  getActivities('NOT_OPEN_TO_PUBLIC')
)

export const activityValidator = (notOpenToPublic: boolean) =>
  notOpenToPublic
    ? yup
        .mixed<ActivityNotOpenToPublicType>()
        .oneOf(activityTypeValuesNotOpenToPublic, 'Activité non valide')
    : yup
        .mixed<ActivityOpenToPublicType>()
        .oneOf(activityTypeValuesOpenToPublic, 'Activité non valide')
