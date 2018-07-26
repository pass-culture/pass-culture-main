import get from 'lodash.get'
import { Form } from 'pass-culture-shared'

import GeoInput from '../components/layout/GeoInput'
import SirenInput from '../components/layout/SirenInput'

Object.assign(Form.WrappedComponent.inputsByType, {
  geo: GeoInput,
  siren: SirenInput,
  siret: SirenInput
})
