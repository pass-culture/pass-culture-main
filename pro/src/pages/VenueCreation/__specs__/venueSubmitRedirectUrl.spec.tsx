import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'

import { venueSubmitRedirectUrl } from '../venueSubmitRedirectUrl'

const offerer = { ...defaultGetOffererResponseModel }

describe('redirect url after submit', () => {
  it('should redirect admin user to the right url', () => {
    const url = venueSubmitRedirectUrl(offerer.id, {
      isAdmin: true,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/structures/1')
  })

  it('redirect non admin user to the right url', () => {
    const url = venueSubmitRedirectUrl(offerer.id, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil?success')
  })
})
