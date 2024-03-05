import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'

import { venueSubmitRedirectUrl } from '../venueSubmitRedirectUrl'

const offerer = { ...defaultGetOffererResponseModel }

describe('redirect url after submit', () => {
  it.each([true, false])(
    `Redirect admin user to the right url, when creation is %s`,
    (creationMode) => {
      const url = venueSubmitRedirectUrl(creationMode, offerer.id, {
        isAdmin: true,
      } as SharedCurrentUserResponseModel)

      expect(url).toEqual('/structures/1')
    }
  )

  it('Redirect non admin user to the right url on creation', () => {
    const url = venueSubmitRedirectUrl(true, offerer.id, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil?success')
  })

  it('Redirect non admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(false, offerer.id, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil')
  })

  it('Redirect admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(false, offerer.id, {
      isAdmin: true,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual(`/structures/${offerer.id}`)
  })

  it('Redirect non admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(false, offerer.id, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil')
  })
})
