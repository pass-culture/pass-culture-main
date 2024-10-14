import { ActivityFormValues } from './ActivityForm'

export const DEFAULT_ACTIVITY_FORM_VALUES: ActivityFormValues = {
  venueTypeCode: '',
  socialUrls: [''],
  targetCustomer: {
    individual: false,
    educational: false,
  },
}

export const activityTargetCustomerCheckboxGroup = [
  {
    label: 'Au grand public',
    name: 'targetCustomer.individual',
  },
  {
    label: 'À des groupes scolaires',
    name: 'targetCustomer.educational',
  },
]
