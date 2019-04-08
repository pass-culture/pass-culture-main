import { Form } from 'pass-culture-shared'

import BicInput from '../components/layout/BicInput'
import Block from '../components/layout/Block'
import GeoInput from '../components/layout/GeoInput'
import IbanInput from '../components/layout/IbanInput'
import SirenInput from '../components/layout/SirenInput'

Object.assign(Form.inputsByType, {
  bic: BicInput,
  iban: IbanInput,
  geo: GeoInput,
  siren: SirenInput,
  siret: SirenInput,
})

Object.assign(Form.defaultProps, {
  BlockComponent: Block,
  handleFailNotification: (state, action) => {
    const {
      payload: { errors },
    } = action
    return (errors && errors[0] && errors[0].global) || 'Formulaire non validé'
  },
  handleSuccessNotification: () => 'Formulaire validé',
})
