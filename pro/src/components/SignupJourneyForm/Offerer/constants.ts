import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'

export const DEFAULT_OFFERER_FORM_VALUES = {
  siret: '',
  name: '',
  publicName: '',
  hasVenueWithSiret: false,
  legalCategoryCode: '',
  ...DEFAULT_ADDRESS_FORM_VALUES,
  isOpenToPublic: '',
}
