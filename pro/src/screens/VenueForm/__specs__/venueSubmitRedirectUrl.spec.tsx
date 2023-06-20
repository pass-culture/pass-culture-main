import { SharedCurrentUserResponseModel } from 'apiClient/v1'

import { IOfferer } from '../../../core/Offerers/types'
import { venueSubmitRedirectUrl } from '../utils/venueSubmitRedirectUrl'

const offerer = { nonHumanizedId: 1 } as IOfferer

describe('redirect url after submit', () => {
  it.each([true, false])(
    `Redirect admin user to the right url, when creation is %s`,
    creationMode => {
      const url = venueSubmitRedirectUrl(creationMode, offerer.nonHumanizedId, {
        isAdmin: true,
      } as SharedCurrentUserResponseModel)

      expect(url).toEqual('/structures/1')
    }
  )

  it('Redirect non admin user to the right url on creation', () => {
    const url = venueSubmitRedirectUrl(true, offerer.nonHumanizedId, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil?success')
  })

  it('Redirect non admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(false, offerer.nonHumanizedId, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil')
  })

  it('Redirect admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(false, offerer.nonHumanizedId, {
      isAdmin: true,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual(`/structures/${offerer.nonHumanizedId}`)
  })

  it('Redirect non admin user to the right url on update', () => {
    const url = venueSubmitRedirectUrl(false, offerer.nonHumanizedId, {
      isAdmin: false,
    } as SharedCurrentUserResponseModel)

    expect(url).toEqual('/accueil')
  })
})
