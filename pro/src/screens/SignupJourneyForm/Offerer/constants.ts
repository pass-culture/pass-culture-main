import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address'

export const DEFAULT_OFFERER_FORM_VALUES = {
  siret: '',
  name: '',
  publicName: '',
  hasVenues: false,
  ...DEFAULT_ADDRESS_FORM_VALUES,
}
