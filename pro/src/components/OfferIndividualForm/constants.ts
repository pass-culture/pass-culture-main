import { ACCESSIBILITY_DEFAULT_VALUES } from './Accessibility/constants'
import { CATEGORIES_DEFAULT_VALUES } from './Categories/constants'
import { EXTERNAL_LINK_DEFAULT_VALUES } from './ExternalLink/constants'
import { INFORMATIONS_DEFAULT_VALUES } from './Informations/constants'
import { NOTIFICATIONS_DEFAULT_VALUES } from './Notifications/constants'
import { OPTION_DUO_DEFAULT_VALUES } from './OptionDuo/constants'
import { USEFUL_INFORMATIONS_DEFAULT_VALUES } from './UsefulInformations/constants'

export const FORM_DEFAULT_VALUES = {
  ...INFORMATIONS_DEFAULT_VALUES,
  ...CATEGORIES_DEFAULT_VALUES,
  ...USEFUL_INFORMATIONS_DEFAULT_VALUES,
  ...ACCESSIBILITY_DEFAULT_VALUES,
  ...NOTIFICATIONS_DEFAULT_VALUES,
  ...OPTION_DUO_DEFAULT_VALUES,
  ...EXTERNAL_LINK_DEFAULT_VALUES,
}
