import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import postInviteMemberAdapter from '../postInviteMemberAdapter'

describe('postInviteMemberAdapter', () => {
  const offererId = 1
  const email = 'new_member@gmail.com'

  it('should return an error when member is already invited', async () => {
    vi.spyOn(api, 'inviteMember').mockRejectedValue(
      new ApiError(
        { method: 'POST' } as ApiRequestOptions,
        {
          status: 400,
          body: {
            email: 'Une invitation a déjà été envoyée à ce collaborateur',
          },
        } as ApiResult,
        ''
      )
    )

    const response = await postInviteMemberAdapter({ offererId, email })

    expect(api.inviteMember).toHaveBeenCalledTimes(1)
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une invitation a déjà été envoyée à ce collaborateur'
    )
    expect(response.payload).toStrictEqual(null)
  })

  it('should return success message', async () => {
    vi.spyOn(api, 'inviteMember').mockResolvedValue()

    const response = await postInviteMemberAdapter({ offererId, email })

    expect(api.inviteMember).toHaveBeenCalledTimes(1)
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe("L'invitation a bien été envoyée.")
    expect(response.payload).toStrictEqual(null)
  })

  it('should return default error message', async () => {
    vi.spyOn(api, 'inviteMember').mockRejectedValue({})

    const response = await postInviteMemberAdapter({ offererId, email })

    expect(api.inviteMember).toHaveBeenCalledTimes(1)
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      "Une erreur est survenue lors de l'envoi de l'invitation."
    )
    expect(response.payload).toStrictEqual(null)
  })
})
