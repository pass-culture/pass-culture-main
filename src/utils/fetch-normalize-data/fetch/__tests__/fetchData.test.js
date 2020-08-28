import { fetchData } from '../fetchData'

const mockSuccess = { foo: 'bar' }

global.fetch = url => {
  if (url.includes('/success')) {
    const response = new Response(JSON.stringify(mockSuccess))
    return response
  }
  if (url.includes('/delayedSuccess')) {
    return new Promise(resolve =>
      setTimeout(() => {
        const response = new Response(JSON.stringify(mockSuccess))
        resolve(response)
      }, 100)
    )
  }
}

describe('src | fetch | fetchData', () => {
  describe('when no fetch timeout', () => {
    it('should return ok true status 200 and datum when url is a success', async () => {
      // given
      const config = {}

      // when
      const result = await fetchData('/success', config)

      // then
      expect(result.ok).toBe(true)
      expect(result.status).toBe(200)
      expect(result.datum).toStrictEqual(mockSuccess)
    })
  })

  describe('when there is a fetch timeout', () => {
    it('should return success when fetchTimeout is above delay', async () => {
      // given
      const config = {
        fetchTimeout: 150,
      }

      // when
      const result = await fetchData('/delayedSuccess', config)

      // then
      expect(result.ok).toBe(true)
      expect(result.status).toBe(200)
      expect(result.datum).toStrictEqual(mockSuccess)
    })
    it('should return fail when gateway timeout is under delay', async () => {
      // given
      const config = {
        fetchTimeout: 50,
      }

      // when
      const result = await fetchData('/delayedSuccess', config)

      // then
      expect(result.ok).toBe(false)
      expect(result.status).toBe(504)
    })
  })
})
