import type { Location } from 'react-router-dom'

import { dehumanizedRoute } from 'utils/dehumanize'

describe('dehumanizedRoute', () => {
  it('should return a dehumanized string for handled parameters', () => {
    const location = {
      pathname: '/my_route_with_parameters/AK/form/12/other/EJ/template/T-GM',
      search: '?structure=EF&unknown=AE&intparam=34',
      hash: '#anchor',
    } as Location
    const matches = [
      {
        data: undefined,
        handle: undefined,
        id: '1',
        params: {
          offererId: 'AK',
          intParam: '12',
          untouchedParam: 'EJ',
          offerId: 'GM',
        },
        pathname: '/my_route_with_parameters/AK/form/12/other/EJ',
      },
    ]
    expect(dehumanizedRoute(location, matches)).toBe(
      '/my_route_with_parameters/2/form/12/other/EJ/template/T-51?structure=33&unknown=AE&intparam=34#anchor'
    )
  })
})
