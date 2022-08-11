import '@testing-library/jest-dom'

import {
  isUrlValid,
  isUrlWithStringInterpolationValid,
  isEmailValid,
} from '../validators'

describe('validators', () => {
  describe('isUrlValid', () => {
    it('should return true for valid urls', () => {
      // given
      const urls = [
        'http://kikou.com',
        null,
        '',
        'https://ABxc123.lol/bla?kikou=bla',
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
        'http://kikou.com?token={token}&email={email}&offerId={offerId}',
      ]

      // when
      const results = urls.map(isUrlValid)

      // then
      expect(results.every(element => element === false)).toBe(true)
    })
  })

  describe('isUrlWithStringInterpolationValid', () => {
    it('should return true for valid urls', () => {
      // given
      const urls = [
        'http://kikou.com',
        null,
        '',
        'https://ABxc123.lol/bla?kikou=bla',
        'http://kikou.com?token={token}&email={email}&offerId={offerId}',
      ]

      // when
      const results = urls.map(isUrlWithStringInterpolationValid)

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
      ]

      // when
      const results = urls.map(isUrlWithStringInterpolationValid)

      // then
      expect(results.every(element => element === false)).toBe(true)
    })
  })

  describe('isEmailValid', () => {
    it('should return true for valid emails', async () => {
      // given
      const emails = ['robert.machin@example.com', null, '']

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
      ]

      // when
      const results = await Promise.all(emails.map(isEmailValid))

      // then
      expect(results.every(element => element === false)).toBe(true)
    })
  })
})
