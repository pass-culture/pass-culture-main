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
