import updateEmail from '../updateEmail'

jest.mock('../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

describe('updateEmail', () => {
  it('should post new email', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    )

    // when
    await updateEmail({ new_email: 'new-email@example.net', password: '123456789' })

    // Then
    expect(global.fetch).toHaveBeenCalledWith('my-localhost/beneficiaries/change_email_request', {
      body: '{"new_email":"new-email@example.net","password":"123456789"}',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'PUT',
    })
  })
})
