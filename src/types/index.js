import { arrayOf, bool, shape, string } from 'prop-types'

export const SelectboxObjectShape = shape({
  label: string.isRequired,
  value: string.isRequired,
})

export const SelectboxObjectType = shape({
  label: string.isRequired,
  options: arrayOf(SelectboxObjectShape),
  value: string,
})

export const FormFooterObject = shape({
  className: string,
  disabled: bool.isRequired,
  id: string,
  label: string.isRequired,
  url: string,
})

export default FormFooterObject
