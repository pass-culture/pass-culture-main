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
    expect(
      getComponentType({
        as: 'button',
        disabled: undefined,
        isExternal: false,
        isSectionLink: false,
      })
    ).toBe('button')
  })

  it('should return "a" when as is "a" and isExternal is true', () => {
    expect(
      getComponentType({
        as: 'a',
        disabled: undefined,
        isExternal: true,
        isSectionLink: false,
      })
    ).toBe('a')
  })

  it('should return "a" when as is "a" and isSectionLink is true', () => {
    expect(
      getComponentType({
        as: 'a',
        disabled: undefined,
        isExternal: false,
        isSectionLink: true,
      })
    ).toBe('a')
  })

  it('should return "a" when as is "a" and disabled is true', () => {
    expect(
      getComponentType({
        as: 'a',
        disabled: true,
        isExternal: false,
        isSectionLink: false,
      })
    ).toBe('a')
  })

  it('should return Link when as is "a" and neither isExternal nor isSectionLink', () => {
    expect(
      getComponentType({
        as: 'a',
        disabled: undefined,
        isExternal: false,
        isSectionLink: false,
      })
    ).toBe(Link)
  })
})

describe('getButtonProps', () => {
  it('should return disabled true and a reset type', () => {
    expect(
      getButtonProps({
        type: 'reset',
        disabled: true,
        isLoading: false,
        onClick: undefined,
      })
    ).toEqual({
      type: 'reset',
      disabled: true,
      onClick: undefined,
    })
  })

  it('should return disabled true when isLoading is true', () => {
    expect(
      getButtonProps({
        type: 'button',
        disabled: false,
        isLoading: true,
        onClick: undefined,
      })
    ).toEqual({
      type: 'button',
      disabled: true,
      onClick: undefined,
    })
  })

  it('should return disabled true when both disabled and isLoading are true', () => {
    expect(
      getButtonProps({
        type: 'button',
        disabled: true,
        isLoading: true,
        onClick: undefined,
      })
    ).toEqual({
      type: 'button',
      disabled: true,
      onClick: undefined,
    })
  })

  it('should return disabled false when both disabled and isLoading are false', () => {
    expect(
      getButtonProps({
        type: 'button',
        disabled: false,
        isLoading: false,
        onClick: undefined,
      })
    ).toEqual({
      type: 'button',
      disabled: false,
      onClick: undefined,
    })
  })

  it('should return onClick when disabled is false', () => {
    const onClick = vi.fn()
    const result = getButtonProps({
      type: 'button',
      disabled: false,
      isLoading: false,
      onClick,
    })
    expect(result.onClick).toBe(onClick)
  })

  it('should return onClick undefined when disabled is true', () => {
    const onClick = vi.fn()
    const result = getButtonProps({
      type: 'button',
      disabled: true,
      isLoading: false,
      onClick,
    })
    expect(result.onClick).toBeUndefined()
  })
})

describe('getAnchorProps', () => {
  it('should return href undefined, aria-disabled, role link and onClick undefined when disabled is true', () => {
    const onClick = vi.fn()
    const result = getAnchorProps({
      absoluteUrl: '/test',
      disabled: true,
      onClick,
      opensInNewTab: false,
    })
    expect(result.href).toBeUndefined()
    expect(result.rel).toBe('noopener noreferrer')
    expect(result.target).toBeUndefined()
    expect(result['aria-disabled']).toBe(true)
    expect(result.role).toBe('link')
    expect(result.onClick).toBeUndefined()
  })

  it('should return href when disabled is false', () => {
    const result = getAnchorProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick: undefined,
      opensInNewTab: false,
    })
    expect(result.href).toBe('/test')
    expect(result.rel).toBe('noopener noreferrer')
    expect(result.target).toBeUndefined()
    expect(result['aria-disabled']).toBeUndefined()
    expect(result.role).toBeUndefined()
  })

  it('should return onClick when disabled is false', () => {
    const onClick = vi.fn()
    const result = getAnchorProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick,
      opensInNewTab: false,
    })
    expect(result.onClick).toBe(onClick)
  })

  it('should return target _blank when opensInNewTab is true', () => {
    const result = getAnchorProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick: undefined,
      opensInNewTab: true,
    })
    expect(result.href).toBe('/test')
    expect(result.target).toBe('_blank')
  })

  it('should return target undefined when opensInNewTab is false', () => {
    const result = getAnchorProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick: undefined,
      opensInNewTab: false,
    })
    expect(result.target).toBeUndefined()
  })
})

describe('getLinkProps', () => {
  it('should return to empty string and onClick undefined when disabled is true', () => {
    const onClick = vi.fn()
    const result = getLinkProps({
      absoluteUrl: '/test',
      disabled: true,
      onClick,
      opensInNewTab: false,
    })
    expect(result.to).toBe('')
    expect(result.target).toBe('_self')
    expect(result.onClick).toBeUndefined()
  })

  it('should return to absoluteUrl when disabled is false', () => {
    const result = getLinkProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick: undefined,
      opensInNewTab: false,
    })
    expect(result.to).toBe('/test')
    expect(result.target).toBe('_self')
  })

  it('should return onClick when disabled is false', () => {
    const onClick = vi.fn()
    const result = getLinkProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick,
      opensInNewTab: false,
    })
    expect(result.onClick).toBe(onClick)
  })

  it('should return target _blank when opensInNewTab is true', () => {
    const result = getLinkProps({
      absoluteUrl: '/test',
      disabled: false,
      onClick: undefined,
      opensInNewTab: true,
    })
    expect(result.to).toBe('/test')
    expect(result.target).toBe('_blank')
  })
})

describe('getComponentProps', () => {
  it('should return button props when Component is "button"', () => {
    const result = getComponentProps({
      Component: 'button',
      type: 'button',
      absoluteUrl: '/test',
      disabled: true,
      isLoading: false,
      onClick: undefined,
      opensInNewTab: false,
    })
    expect(result).toEqual({
      disabled: true,
      type: 'button',
      onClick: undefined,
    })
  })

  it('should return submit button props when Component is "button"', () => {
    const result = getComponentProps({
      Component: 'button',
      type: 'submit',
      absoluteUrl: '/test',
      disabled: true,
      isLoading: false,
      onClick: undefined,
      opensInNewTab: false,
    })
    expect(result).toEqual({
      disabled: true,
      type: 'submit',
      onClick: undefined,
    })
  })

  it('should return anchor props when Component is "a"', () => {
    const result = getComponentProps({
      Component: 'a',
      type: 'button',
      absoluteUrl: '/test',
      disabled: false,
      isLoading: false,
      onClick: undefined,
      opensInNewTab: true,
    })
    expect(result).toEqual({
      href: '/test',
      rel: 'noopener noreferrer',
      target: '_blank',
      'aria-disabled': undefined,
      onClick: undefined,
      role: undefined,
    })
  })

  it('should return link props when Component is Link', () => {
    const result = getComponentProps({
      Component: Link,
      type: 'button',
      absoluteUrl: '/test',
      disabled: false,
      isLoading: false,
      onClick: undefined,
      opensInNewTab: true,
    })
    expect(result).toEqual({
      to: '/test',
      target: '_blank',
      rel: 'noopener noreferrer',
      onClick: undefined,
    })
  })
})
