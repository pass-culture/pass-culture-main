import type { EditVenueBodyModel } from '@/apiClient/v1'
import type { PickDefined } from '@/commons/utils/types'

export type EditVenueBodyModelNotificationsPatch = PickDefined<
  EditVenueBodyModel,
  'bookingEmail'
>
