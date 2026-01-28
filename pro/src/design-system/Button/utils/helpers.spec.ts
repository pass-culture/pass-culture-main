import { Link } from 'react-router'

import {
  getAnchorProps,
  getButtonProps,
  getComponentProps,
  getComponentType,
  getLinkProps,
} from './helpers'

describe('getComponentType', () => {
  it('should return "button" when as is "button"', () => {
    expect(getComponentType('button', false, false)).toBe('button')
  })

  it('should return "a" when as is "a" and isExternal is true', () => {
    expect(getComponentType('a', true, false)).toBe('a')
  })

  it('should return "a" when as is "a" and isSectionLink is true', () => {
    expect(getComponentType('a', false, true)).toBe('a')
  })

  it('should return Link when as is "a" and neither isExternal nor isSectionLink', () => {
    expect(getComponentType('a', false, false)).toBe(Link)
  })
})

describe('getButtonProps', () => {
  it('should return disabled true and a reset type', () => {
    expect(getButtonProps('reset', true, false)).toEqual({
      type: 'reset',
      disabled: true,
    })
  })

  it('should return disabled true when isLoading is true', () => {
    expect(getButtonProps('button', false, true)).toEqual({
      type: 'button',
      disabled: true,
    })
  })

  it('should return disabled true when both disabled and isLoading are true', () => {
    expect(getButtonProps('button', true, true)).toEqual({
      type: 'button',
      disabled: true,
    })
  })

  it('should return disabled false when both disabled and isLoading are false', () => {
    expect(getButtonProps('button', false, false)).toEqual({
      type: 'button',
      disabled: false,
    })
  })
})

describe('getAnchorProps', () => {
  it('should return href undefined when disabled is true', () => {
    const result = getAnchorProps('/test', true, false)
    expect(result.href).toBeUndefined()
    expect(result.rel).toBe('noopener noreferrer')
    expect(result.target).toBeUndefined()
    expect(result['aria-disabled']).toBe(true)
  })

  it('should return href when disabled is false', () => {
    const result = getAnchorProps('/test', false, false)
    expect(result.href).toBe('/test')
    expect(result.rel).toBe('noopener noreferrer')
    expect(result.target).toBeUndefined()
    expect(result['aria-disabled']).toBeUndefined()
  })

  it('should return target _blank when opensInNewTab is true', () => {
    const result = getAnchorProps('/test', false, true)
    expect(result.href).toBe('/test')
    expect(result.target).toBe('_blank')
  })

  it('should return target undefined when opensInNewTab is false', () => {
    const result = getAnchorProps('/test', false, false)
    expect(result.target).toBeUndefined()
  })
})

describe('getLinkProps', () => {
  it('should return to empty string when disabled is true', () => {
    const result = getLinkProps('/test', true, false)
    expect(result.to).toBe('')
    expect(result.target).toBeUndefined()
  })

  it('should return to absoluteUrl when disabled is false', () => {
    const result = getLinkProps('/test', false, false)
    expect(result.to).toBe('/test')
    expect(result.target).toBeUndefined()
  })

  it('should return target _blank when opensInNewTab is true', () => {
    const result = getLinkProps('/test', false, true)
    expect(result.to).toBe('/test')
    expect(result.target).toBe('_blank')
  })
})

describe('getComponentProps', () => {
  it('should return button props when Component is "button"', () => {
    const result = getComponentProps(
      'button',
      'button',
      '/test',
      true,
      false,
      false
    )
    expect(result).toEqual({ disabled: true, type: 'button' })
  })

  it('should return submit button props when Component is "button"', () => {
    const result = getComponentProps(
      'button',
      'submit',
      '/test',
      true,
      false,
      false
    )
    expect(result).toEqual({ disabled: true, type: 'submit' })
  })

  it('should return anchor props when Component is "a"', () => {
    const result = getComponentProps(
      'a',
      undefined,
      '/test',
      false,
      false,
      true
    )
    expect(result).toEqual({
      href: '/test',
      rel: 'noopener noreferrer',
      target: '_blank',
      'aria-disabled': undefined,
    })
  })

  it('should return link props when Component is Link', () => {
    const result = getComponentProps(
      Link,
      undefined,
      '/test',
      false,
      false,
      true
    )
    expect(result).toEqual({
      to: '/test',
      target: '_blank',
    })
  })
})
