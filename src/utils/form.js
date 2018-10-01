import get from 'lodash.get'
import { Block, Form } from 'pass-culture-shared'

import GeoInput from '../components/layout/GeoInput'
import SirenInput from '../components/layout/SirenInput'
import BicInput from '../components/layout/BicInput'
import IbanInput from '../components/layout/IbanInput'

Object.assign(Form.inputsByType, {
  geo: GeoInput,
  siren: SirenInput,
  siret: SirenInput,
  bic: BicInput,
  iban: IbanInput,
})

Object.assign(Form.defaultProps, {
  BlockComponent: Block,
  handleFailNotification: (state, action) =>
    get(action, 'errors.0.global') || 'Formulaire non validé',
  handleSuccessNotification: () => 'Formulaire validé',
})
