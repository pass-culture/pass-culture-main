import { client } from 'repository/pcapi/pcapiClient'
import type { MockInstance } from 'vitest'

import { API_URL } from '@/commons/utils/config'

describe('pcapiClient', () => {
  let fetchSpy: MockInstance<typeof fetch>

  beforeEach(() => {
    fetchSpy = vi.spyOn(global, 'fetch')
  })

  afterEach(() => {
    fetchSpy.mockRestore()
  })

  describe('postWithFormData', () => {
    it('should call API with given path and formData and credentials by default and correct method', async () => {
      // Given
      const path = '/mediations'
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('offererId', 'BB')
      body.append('credit', 'Mon crédit')
      body.append('croppingRect[x]', '12')
      body.append('croppingRect[y]', '32')
      body.append('croppingRect[height]', '350')
      body.append('thumb', file)

      // When
      await client.postWithFormData(path, body)

      // Then
      expect(fetchSpy).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        headers: { encode: 'multipart/form-data' },
        method: 'POST',
        body: body,
      })
    })

    it('should call API without credentials when not required', async () => {
      // Given
      const path = '/mediations'
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('offererId', 'BB')
      body.append('credit', 'Mon crédit')
      body.append('croppingRect[x]', '12')
      body.append('croppingRect[y]', '32')
      body.append('croppingRect[height]', '350')
      body.append('thumb', file)

      // When
      await client.postWithFormData(path, body, false)

      // Then (no credentials when not required)
      expect(fetchSpy).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: { encode: 'multipart/form-data' },
        method: 'POST',
        body: body,
      })
    })
  })
})
