import type { Decorator } from 'final-form'
import createDecorator from 'final-form-calculate'

import { CreateOffererQueryModel } from 'apiClient/v1'
import { getSirenDataAdapter } from 'core/Offerers/adapters'

export const sirenUpdate = async (humanSiren: string) => {
  const response = await getSirenDataAdapter(humanSiren)
  if (!response.isOk) {
    return {
      address: '',
      city: '',
      name: '',
      postalCode: '',
      siren: humanSiren,
      apeCode: '',
    }
  }
  let values = undefined
  if (response.payload.values != null) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { apeCode, ...rest } = response.payload.values
    values = rest
  }
  return values
}

export const addressAndDesignationFromSirenDecorator = createDecorator({
  field: 'siren',
  updates: sirenUpdate,
}) as Decorator<CreateOffererQueryModel>
