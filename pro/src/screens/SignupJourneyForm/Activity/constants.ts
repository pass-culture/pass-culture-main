import { Target } from 'apiClient/v1'

export const DEFAULT_ACTIVITY_FORM_VALUES = {
  venueType: '',
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
