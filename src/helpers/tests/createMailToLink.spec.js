import createMailToLink from '../createMailToLink'

describe('src | helpers | createMailToLink ', () => {
  it('should create a new link for window location href', () => {
    // given
    const email = 'email@fake.url'
    const headers = {
      body: 'http://localhost:3000/decouverte/AE/?shared_by=AE',
      subject: 'Fake Title',
    }

    // when
    const result = createMailToLink(email, headers)

    // then
    expect(result).toStrictEqual(
      'mailto:email@fake.url?body=http%3A%2F%2Flocalhost%3A3000%2Fdecouverte%2FAE%2F%3Fshared_by%3DAE&subject=Fake%20Title'
    )
  })

  it('should create an empty link for window location href', () => {
    // given
    const email = null
    const headers = {
      body: 'http://localhost:3000/decouverte/AE/?shared_by=AE',
      subject: 'Fake Title',
    }

    // when
    const result = createMailToLink(email, headers)

    // then
    expect(result).toStrictEqual(
      'mailto:?body=http%3A%2F%2Flocalhost%3A3000%2Fdecouverte%2FAE%2F%3Fshared_by%3DAE&subject=Fake%20Title'
    )
  })

  it('should create an empty link without headers', () => {
    // given
    const email = null
    const headers = null

    // when
    const result = createMailToLink(email, headers)

    // then
    expect(result).toStrictEqual('mailto:')
  })
})
