export const defaultActivityFormValues = (isNewSignupEnabled: boolean) => {
  return {
    venueTypeCode: '',
    socialUrls: [''],
    targetCustomer: {
      individual: false,
      educational: false,
    },
    phoneNumber: isNewSignupEnabled ? '' : undefined,
  }
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
