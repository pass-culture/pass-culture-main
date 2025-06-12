
export const defaultActivityFormValues = (isNewSignupEnabled: boolean) => {
  return {
    venueTypeCode: '',
    socialUrls: [{url: ''}],
    targetCustomer: {
      individual: false,
      educational: false,
    },
    phoneNumber: isNewSignupEnabled ? '' : undefined,
  }
}
