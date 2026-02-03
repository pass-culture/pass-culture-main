import type { StudentLevels } from '@/apiClient/v1'
import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'

export type CollectiveDataFormValues = {
  collectiveDescription?: string
  collectiveStudents?: StudentLevels[]
  collectiveWebsite?: string
  collectivePhone?: string
  collectiveEmail?: string
  collectiveDomains?: string[]
  collectiveLegalStatus?: string
  collectiveInterventionArea?: string[]
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
}
