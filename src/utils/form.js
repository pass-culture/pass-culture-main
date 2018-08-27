import get from 'lodash.get'
import { Block, Form } from 'pass-culture-shared'

import GeoInput from '../components/layout/GeoInput'
import SirenInput from '../components/layout/SirenInput'

Object.assign(Form.inputsByType, {
  geo: GeoInput,
  siren: SirenInput,
  siret: SirenInput,
})

Object.assign(Form.defaultProps, {
  BlockComponent: Block,
  handleFailNotification: (state, action) =>
    get(action, 'errors.0.global') || 'Formulaire non validé',
  handleSuccessNotification: () => 'Formulaire validé',
})
