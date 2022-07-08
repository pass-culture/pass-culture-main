import { CollectiveDataFormValues } from '../CollectiveDataForm/type'
import { GetVenueResponseModel } from 'apiClient/v1'
import { api } from 'apiClient/api'

type EditVenueCollectiveDataAdapter = Adapter<
  { venueId: string; values: CollectiveDataFormValues },
  GetVenueResponseModel,
  GetVenueResponseModel[]
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
    })
    return {
      isOk: true,
      message: '',
      payload: response,
    }
  } catch (e) {
    return {
      isOk: false,
      message: 'Une erreur est surevenue lors de l’enregistrement des données',
      payload: [],
    }
  }
}

export default editVenueCollectiveDataAdapter
