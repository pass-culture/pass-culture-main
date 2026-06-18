import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
  StudentLevels,
} from '@/apiClient/v1'

export type CollectiveDataFormValues = {
  collectiveDescription?: string
  collectiveStudents?: StudentLevels[]
  collectiveWebsite?: string
  collectivePhone?: string
  collectiveEmail?: string
  collectiveDomains?: string[]
  collectiveLegalStatus?: string
  collectiveInterventionArea?: string[]
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic | null
}
