import { Target } from 'apiClient/v1'

import { IActivityFormValues } from './ActivityForm'

export const DEFAULT_ACTIVITY_FORM_VALUES: IActivityFormValues = {
  venueTypeCode: '',
  socialUrls: [''],
  targetCustomer: undefined,
}

export const activityTargetCustomerTypeRadios = [
  {
    label: 'À destination du grand public',
    value: Target.INDIVIDUAL,
  },
  {
    label: "À destination d'un groupe scolaire",
    value: Target.EDUCATIONAL,
  },
  {
    label: 'Les deux',
    value: Target.INDIVIDUAL_AND_EDUCATIONAL,
  },
]
