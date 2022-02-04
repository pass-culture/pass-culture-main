import { removeWhitespaces } from 'react-final-form-utils'

import formatSiren from 'components/layout/form/fields/SirenField/formatSiren'

import getSirenInformation from './getSirenInformation'

export const bindAddressAndDesignationFromSiren = async siren => {
  const formattedSiren = formatSiren(siren)
  const sirenFormatForAPI = removeWhitespaces(formattedSiren)

  if (sirenFormatForAPI.length === 9) {
    const message = await getSirenInformation(sirenFormatForAPI)
    return { ...message, siren: formattedSiren }
  } else {
    return {
      address: '',
      city: '',
      name: '',
      postalCode: '',
      siren,
    }
  }
}

export default bindAddressAndDesignationFromSiren
