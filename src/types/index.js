import { bool, shape, string } from 'prop-types'

export const FormFooterObject = shape({
  className: string,
  disabled: bool.isRequired,
  id: string,
  label: string.isRequired,
  url: string,
})

export default FormFooterObject
