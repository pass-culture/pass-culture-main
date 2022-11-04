import { DEFAULT_FORM_VALUES } from '../constants'
import { IVenueFormValues } from '../types'

const setDefaultInitialFormValues = (): IVenueFormValues => {
  return { ...DEFAULT_FORM_VALUES }
}

export default setDefaultInitialFormValues
