import { Form } from 'pass-culture-shared'

import BicInput from '../components/layout/BicInput'
import BlockContainer from '../components/layout/BlockContainer'
import IbanInput from '../components/layout/IbanInput'

Object.assign(Form.inputsByType, {
  bic: BicInput,
  iban: IbanInput,
})

Object.assign(Form.defaultProps, {
  blockComponent: BlockContainer,
  handleFailNotification: (state, action) => {
    const {
      payload: { errors },
    } = action
    return (errors && errors[0] && errors[0].global) || 'Formulaire non validé'
  },
  handleSuccessNotification: () => 'Formulaire validé',
})
