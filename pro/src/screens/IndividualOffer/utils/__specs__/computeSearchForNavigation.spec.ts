import { computeSearchForNavigation } from '../computeSearchForNavigation'

describe('computeSearchForNavigation', () => {
  const testedElements = [
    { input: 'structure=123&lieu=456', expected: 'structure=123&lieu=456' },
    { input: 'structure=123&somethingUseless=456', expected: 'structure=123' },
    { input: 'somethingUseless=456', expected: '' },
    { input: '', expected: '' },
  ]
  it.each(testedElements)('should compute right search when %s', element => {
    expect(computeSearchForNavigation(element.input)).toBe(element.expected)
  })
})
