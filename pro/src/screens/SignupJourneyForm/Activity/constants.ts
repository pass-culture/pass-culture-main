export const DEFAULT_ACTIVITY_FORM_VALUES = {
  venueType: '',
  socialUrls: [''],
  targetCustomer: null,
}

export enum TargetCustomerTypeEnum {
  ALL = 'all',
  INDIVIDUAL = 'individual',
  COLLECTIVE = 'collective',
}

export const activityTargetCustomerTypeRadios = [
  {
    label: 'À destination du grand public',
    value: TargetCustomerTypeEnum.INDIVIDUAL,
  },
  {
    label: "À destination d'un groupe scolaire",
    value: TargetCustomerTypeEnum.COLLECTIVE,
  },
  {
    label: 'Les deux',
    value: TargetCustomerTypeEnum.ALL,
  },
]
