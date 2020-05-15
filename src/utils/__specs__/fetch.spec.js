import { fetchFromApiWithCredentials } from '../fetch'
import { API_URL } from '../config'

describe('fetchFromApiWithCredentials', () => {
  let mockFetchPromise
  let fetchMock

  beforeEach(() => {
    mockFetchPromise = Promise.resolve({
      ok: true,
      json: () => Promise.resolve([]),
    })
    fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() => mockFetchPromise)
  })

  afterEach(() => {
    fetchMock.mockClear()
  })

  it('should call API with given path with credentials', async () => {
    // Given
    const path = '/bookings/pro'

    // When
    await fetchFromApiWithCredentials(path)

    // Then
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}${path}`, { credentials: 'include' })
  })

  it('should add "/" at beginning of path if not present', async () => {
    // Given
    const path = 'bookings/pro'

    // When
    await fetchFromApiWithCredentials(path)

    // Then
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/${path}`, { credentials: 'include' })
  })

  it('should return json if return status is ok', async () => {
    // Given
    const oneBooking = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    mockFetchPromise = Promise.resolve({
      ok: true,
      json: () => Promise.resolve([oneBooking]),
    })

    // When
    const response = await fetchFromApiWithCredentials('/bookings/pro')

    // Then
    expect(response).toHaveLength(1)
    expect(response).toStrictEqual([oneBooking])
  })

  it('should reject promise if return status is not ok', async () => {
    // Given
    mockFetchPromise = Promise.resolve({
      ok: false,
    })

    // When
    const response = fetchFromApiWithCredentials('/bookings/pro')

    // Then
    await expect(response).rejects.toThrow('HTTP error')
  })
})
