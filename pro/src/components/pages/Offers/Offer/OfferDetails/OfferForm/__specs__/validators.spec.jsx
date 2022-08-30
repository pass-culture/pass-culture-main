import '@testing-library/jest-dom'

import { isUrlValid, isEmailValid } from '../validators'

describe('validators', () => {
  describe('isUrlValid', () => {
    it('should return true for valid urls', () => {
      // given
      const urls = [
        'http://kikou.com',
        'http://kikou.com/',
        'https://kikou.com/',
        'http://www.kikou.com/',
        'http://kikou_lol.com',
        'http://kikou@lol.com',
        null,
        '',
        'http://182.168.1.200',
        'http://182.168.1.200/M/lol/blabla/fiche.php?&typearticle=68092',
        'http://kikou--lol.com',
        'http://KIKOU_lol.com',
        'https://kikou.com/évêöù?%$£()Æ&«»""숲',
        'http://kikou.com?token={token}&email={email}&offerId={offerId}',
      ]

      // when
      const results = urls.map(isUrlValid)

      // then
      expect(results.every(element => element === true)).toBe(true)
    })

    it('should return false for invalid urls', () => {
      // given
      const urls = [
        'kikou.com',
        'http://kikou',
        'http://.com',
        'http://kikou.c',
        'http://kik&$ou.com',
        ' http://kikou.com',
        'http://kikou.com ',
        'http://kikou.com http://kikou.com',
        'http://kikou.com?token={token}&email={email}& offerId={offerId}',
      ]

      // when
      const results = urls.map(isUrlValid)

      // then
      expect(results.every(element => element === false)).toBe(true)
    })
  })

  describe('isEmailValid', () => {
    it('should return true for valid emails', async () => {
      // given
      const emails = [
        'robert.machin@example.com',
        null,
        '',
        'robert.machin+@example.com',
        '+robert.machin+@example.com',
        'Robert-Machin@example.net',
      ]

      // when
      const results = await Promise.all(emails.map(isEmailValid))

      // then
      expect(results.every(element => element === true)).toBe(true)
    })

    it('should return false for invalid emails', async () => {
      // given
      const emails = [
        'robert.machin@example.',
        '@example.com',
        'robert.machin@com',
        'robert.machinexample.com',
        'robert.machin@example.com ',
        'robert.machin@example.com robert2.machin@example.com',
        'plainaddress',
        '#@%^%#$@#$@#.com',
        '@example.com',
        'Joe Smith <email@example.com>',
        'email.example.com',
        'email@example@example.com',
        '.email@example.com',
        'email.@example.com',
        'email..email@example.com',
        'email@example.com (Joe Smith)',
        'email@example',
        'email@-example.com',
        'email@111.222.333.44444',
        'email@example..com',
        'Abc..123@example.com',
      ]

      // when
      const results = await Promise.all(emails.map(isEmailValid))

      // then
      expect(results.every(element => element === false)).toBe(true)
    })
  })
})
