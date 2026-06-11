import type { EditVenueBodyModel } from '@/apiClient/v1/new'
import type { PickDefined } from '@/commons/utils/types'

export type EditVenueBodyModelNotificationsPatch = PickDefined<
  EditVenueBodyModel,
  'bookingEmail'
>
