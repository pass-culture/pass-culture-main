/* eslint no-console: 0, max-nested-callbacks: 0 */
import { expect } from 'chai'

import MyHelper from './my/helper/relative/path'

describe('My helper name', function() {
  beforeEach(function() {})
  afterEach(function() {})
  describe('MyHelper.method()', function() {
    it('it expect something', function() {
      const value = ''
      const expected = ''
      const result = MyHelper.method(value)
      expect(expected).to.equal(result)
    })
    it('it expect something with exception', function() {
      expect(function() {
        MyHelper.method()
      }).to.throw()
    })
    it('it expect something with promise', function(done) {
      MyHelper.method()
        .then(result => {
          expect(result).to.equal('promise resolved')
        })
        .finally(done)
    })
  })
})
