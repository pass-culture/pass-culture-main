import type {
  EditVenueBodyModel,
  VenueContactModelV2,
} from '@/apiClient/v1/new'
import type { Defined, PickDefined } from '@/commons/utils/types'

export type EditVenueBodyModelVenueEditionPatch = PickDefined<
  EditVenueBodyModel,
  | 'activity'
  | 'audioDisabilityCompliant'
  | 'culturalDomains'
  | 'isOpenToPublic'
  | 'mentalDisabilityCompliant'
  | 'motorDisabilityCompliant'
  | 'openingHours'
  | 'visualDisabilityCompliant'
  | 'volunteeringUrl'
> & {
  contact: Defined<VenueContactModelV2>
}
