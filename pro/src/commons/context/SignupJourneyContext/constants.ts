import { ActivityContext } from './SignupJourneyContext'

export const DEFAULT_ACTIVITY_VALUES: ActivityContext = {
  venueTypeCode: '',
  socialUrls: [''],
  targetCustomer: undefined,
  phoneNumber: undefined,
}

const DEFAULT_ACTIVITY_VALUES_WITH_PHONE: ActivityContext = {
  ...DEFAULT_ACTIVITY_VALUES,
  phoneNumber: '',
}

export const defaultActivityValues = (isNewSignupEnabled: boolean) => {
  return isNewSignupEnabled
    ? DEFAULT_ACTIVITY_VALUES_WITH_PHONE
    : DEFAULT_ACTIVITY_VALUES
}
