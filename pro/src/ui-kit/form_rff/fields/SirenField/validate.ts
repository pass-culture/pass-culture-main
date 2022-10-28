import { getSirenDataAdapter } from 'core/Offerers/adapters'
import { composeValidators } from 'utils/react-final-form'

const required = (value: string) => {
  return value ? undefined : 'Ce champ est obligatoire'
}

const mustHaveTheProperLength = (value: string) => {
  return value.length < 9 ? 'SIREN trop court' : undefined
}

export const existsInINSEERegistry = async (
  value: string
): Promise<string | void> => {
  const response = await getSirenDataAdapter(value)
  return response.isOk ? undefined : response.message
}

export default composeValidators(
  required,
  mustHaveTheProperLength,
  existsInINSEERegistry
)
