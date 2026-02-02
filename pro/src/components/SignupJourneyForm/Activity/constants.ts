import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'

export const defaultActivityFormValues: ActivityFormValues = {
  activity: undefined,
  socialUrls: [{ url: '' }],
  targetCustomer: {
    individual: false,
    educational: false,
  },
  phoneNumber: '',
  culturalDomains: undefined,
}
