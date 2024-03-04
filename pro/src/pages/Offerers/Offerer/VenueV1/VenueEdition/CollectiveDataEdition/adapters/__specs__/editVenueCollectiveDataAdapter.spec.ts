import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { defaultGetVenue } from 'utils/collectiveApiFactories'

import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from '../../CollectiveDataForm/initialValues'
import editVenueCollectiveDataAdapter from '../editVenueCollectiveDataAdapter'

describe('editVenueCollectiveDataAdapter', () => {
  it('should return error message', async () => {
    vi.spyOn(api, 'editVenueCollectiveData').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 500 } as ApiResult, '')
    )

    expect(
      await editVenueCollectiveDataAdapter({
        venueId: 1,
        values: {
          ...COLLECTIVE_DATA_FORM_INITIAL_VALUES,
          collectiveDescription: 'blabla',
        },
      })
    ).toStrictEqual({
      isOk: false,
      payload: null,
      message: 'Une erreur est survenue lors de l’enregistrement des données',
    })
  })

  it('should return success message', async () => {
    const venueId = 1
    vi.spyOn(api, 'editVenueCollectiveData').mockResolvedValueOnce({
      ...defaultGetVenue,
    })
    const response = await editVenueCollectiveDataAdapter({
      venueId: venueId,
      values: {
        ...COLLECTIVE_DATA_FORM_INITIAL_VALUES,
        collectiveDescription: 'blabla',
        collectiveDomains: ['1'],
        collectiveLegalStatus: '3',
      },
    })

    expect(response).toStrictEqual({
      isOk: true,
      payload: { ...defaultGetVenue, id: venueId },
      message: 'Vos informations ont bien été enregistrées',
    })
    expect(api.editVenueCollectiveData).toHaveBeenCalledWith(venueId, {
      ...COLLECTIVE_DATA_FORM_INITIAL_VALUES,
      collectiveDescription: 'blabla',
      collectiveDomains: [1],
      venueEducationalStatusId: 3,
      collectiveLegalStatus: '3',
    })
  })
})
