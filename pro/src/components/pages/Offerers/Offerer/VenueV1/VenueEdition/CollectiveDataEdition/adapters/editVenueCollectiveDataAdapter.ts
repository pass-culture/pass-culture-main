import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'

import { CollectiveDataFormValues } from '../CollectiveDataForm/type'

type EditVenueCollectiveDataAdapter = Adapter<
  { venueId: string; values: CollectiveDataFormValues },
  GetVenueResponseModel,
  null
>

const editVenueCollectiveDataAdapter: EditVenueCollectiveDataAdapter = async ({
  venueId,
  values,
}) => {
  try {
    const response = await api.editVenue(venueId, {
      ...values,
      collectiveDomains: values.collectiveDomains.map(stringId =>
        Number(stringId)
      ),
      venueEducationalStatusId: values.collectiveLegalStatus
        ? Number(values.collectiveLegalStatus)
        : null,
    })
    return {
      isOk: true,
      message: 'Vos informations ont bien été enregistrées',
      payload: response,
    }
  } catch (e) {
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de l’enregistrement des données',
      payload: null,
    }
  }
}

export default editVenueCollectiveDataAdapter
