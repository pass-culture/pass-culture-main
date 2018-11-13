import createMailToLink from '../utils'

describe('src | components | share | utils ', () => {
  describe('createMailToLink ', () => {
    it('should create a new link for window location href', () => {
      // given
      const headers = {
        body: 'http://localhost:3000/decouverte/AE/?shared_by=AE',
        subject: 'Fake Title',
      }

      // when
      const result = createMailToLink('email@fake.url', headers)

      // then
      expect(result).toEqual(
        'mailto:email@fake.url?body=http%3A%2F%2Flocalhost%3A3000%2Fdecouverte%2FAE%2F%3Fshared_by%3DAE&subject=Fake%20Title'
      )
    })
  })
})
