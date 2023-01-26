import * as pcapi from 'repository/pcapi/pcapi'

import { getEducationalDomainsOptionsAdapter } from '../getEducationalDomainsOptionsAdapter'

describe('getEducationalDomainsOptionsAdapter', () => {
  it('should return an error when server responds with an error', async () => {
    // given
    jest.spyOn(pcapi, 'getEducationalDomains').mockRejectedValueOnce({
      status: 500,
    })

    // when
    const response = await getEducationalDomainsOptionsAdapter()

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Nous avons rencontré un problème lors du chargemement des données'
    )
  })

  it('should return domains options when the api call was successful', async () => {
    // given
    jest.spyOn(pcapi, 'getEducationalDomains').mockResolvedValueOnce([
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
      { id: 3, name: 'Arts' },
    ])

    // when
    const response = await getEducationalDomainsOptionsAdapter()

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.payload).toStrictEqual([
      { value: 1, label: 'Danse' },
      { value: 2, label: 'Architecture' },
      { value: 3, label: 'Arts' },
    ])
  })
})
