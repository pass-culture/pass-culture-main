import { ApiError, GetVenueResponseModel } from 'apiClient/v1'

import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from '../../CollectiveDataForm/initialValues'
import { api } from 'apiClient/api'
import editVenueCollectiveDataAdapter from '../editVenueCollectiveDataAdapter'

describe('editVenueCollectiveDataAdapter', () => {
  it('should return error message', async () => {
    jest
      .spyOn(api, 'editVenue')
      .mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 500 } as ApiResult, '')
      )

    expect(
      await editVenueCollectiveDataAdapter({
        venueId: 'A1',
        values: {
          ...COLLECTIVE_DATA_FORM_INITIAL_VALUES,
          collectiveDescription: 'blabla',
        },
      })
    ).toStrictEqual({
      isOk: false,
      payload: null,
      message: 'Une erreur est surevenue lors de l’enregistrement des données',
    })
  })

  it('should return success message', async () => {
    jest
      .spyOn(api, 'editVenue')
      .mockResolvedValueOnce({ id: 'A1' } as GetVenueResponseModel)

    const response = await editVenueCollectiveDataAdapter({
      venueId: 'A1',
      values: {
        ...COLLECTIVE_DATA_FORM_INITIAL_VALUES,
        collectiveDescription: 'blabla',
        collectiveDomains: ['1'],
        collectiveLegalStatus: '3',
      },
    })

    expect(response).toStrictEqual({
      isOk: true,
      payload: { id: 'A1' },
      message: 'Vos informations ont bien été enregistrées',
    })
    expect(api.editVenue).toHaveBeenCalledWith('A1', {
      ...COLLECTIVE_DATA_FORM_INITIAL_VALUES,
      collectiveDescription: 'blabla',
      collectiveDomains: [1],
      collectiveLegalStatus: 3,
    })
  })
})
