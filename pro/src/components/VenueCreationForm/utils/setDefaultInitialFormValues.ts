import { DEFAULT_FORM_VALUES } from '../constants'
import { VenueFormValues } from '../types'

const setDefaultInitialFormValues = (): VenueFormValues => {
  return { ...DEFAULT_FORM_VALUES }
}

export default setDefaultInitialFormValues
