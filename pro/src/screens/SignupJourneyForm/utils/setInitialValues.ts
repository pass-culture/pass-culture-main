import { DEFAULT_SIGNUP_JOURNEY_FORM_VALUES } from '../constants'
import { ISignupJourneyFormValues } from '../types'

const setDefaultInitialFormValues = (): ISignupJourneyFormValues => {
  return { ...DEFAULT_SIGNUP_JOURNEY_FORM_VALUES }
}

export default setDefaultInitialFormValues
