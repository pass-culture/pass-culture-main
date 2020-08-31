import { handleEditPasswordSubmit } from '../handleEditPasswordSubmit'

jest.mock('../../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

const formValues = {}
const handleSubmitFail = jest.fn()
const handleSubmitSuccess = jest.fn()

describe('when response from API', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('should call fetch properly', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    )

    // when
    await handleEditPasswordSubmit(formValues, handleSubmitFail, handleSubmitSuccess)

    // Then
    expect(global.fetch).toHaveBeenCalledWith('my-localhost/users/current/change-password', {
      body: JSON.stringify(formValues),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'POST',
    })
  })

  it('should call success function', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
        ok: true,
      })
    )

    // when
    await handleEditPasswordSubmit(formValues, handleSubmitFail, handleSubmitSuccess)

    // Then
    expect(handleSubmitSuccess).toHaveBeenCalledTimes(1)
  })
})

describe('when status is 400', () => {
  it('should call fail function', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({ errors: ['error message'] }),
        status: 400,
      })
    )

    // when
    await handleEditPasswordSubmit(formValues, handleSubmitFail, handleSubmitSuccess)

    // Then
    expect(handleSubmitFail).toHaveBeenCalledWith({ errors: ['error message'] })
  })
})

describe('when status is other that 400', () => {
  it('should stop the app', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
        ok: false,
        status: 582,
        statusText: 'Error',
      })
    )

    // When
    const expected = handleEditPasswordSubmit(formValues, handleSubmitFail, handleSubmitSuccess)

    // Then
    await expect(expected).rejects.toThrow('Status: 582, Status text: Error')
  })
})

describe('when no response from API', () => {
  it('should stop the app', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() => Promise.reject('API is down'))

    // when
    const expected = handleEditPasswordSubmit(formValues, handleSubmitFail, handleSubmitSuccess)

    // Then
    await expect(expected).rejects.toThrow('API is down')
  })
})
