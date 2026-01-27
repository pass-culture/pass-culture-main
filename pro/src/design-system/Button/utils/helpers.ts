import { Link } from 'react-router'

import type { ButtonTypeAttribute } from '../types'

/**
 * Get the component type.
 * @param as - The component type.
 * @param isExternal - If true, the component will be external.
 * @param isSectionLink - If true, the component will be a section link.
 * @returns The component type.
 */
export const getComponentType = (
  as: 'button' | 'a',
  isExternal: boolean,
  isSectionLink: boolean
): React.ElementType => {
  if (as === 'button') {
    return 'button'
  }
  if (isExternal || isSectionLink) {
    return 'a'
  }
  return Link
}

/**
 * Get the props for the button.
 * @param disabled - If true, the button will be disabled.
 * @param isLoading - If true, the button will be loading.
 * @returns The props for the button.
 */
export const getButtonProps = (
  type: ButtonTypeAttribute,
  disabled?: boolean,
  isLoading?: boolean
) => {
  return { type, disabled: disabled || isLoading }
}

/**
 * Get the props for the anchor.
 * @param absoluteUrl - The absolute URL.
 * @param disabled - If true, the anchor will be disabled.
 * @param opensInNewTab - If true, the anchor will open in a new tab.
 * @returns The props for the anchor.
 */
export const getAnchorProps = (
  absoluteUrl: string,
  disabled?: boolean,
  opensInNewTab?: boolean
) => {
  return {
    href: disabled ? undefined : absoluteUrl,
    rel: 'noopener noreferrer',
    target: opensInNewTab ? '_blank' : undefined,
    'aria-disabled': disabled || undefined,
  }
}

/**
 * Get the props for the link.
 * @param absoluteUrl - The absolute URL.
 * @param disabled - If true, the link will be disabled.
 * @param opensInNewTab - If true, the link will open in a new tab.
 * @returns The props for the link.
 */
export const getLinkProps = (
  absoluteUrl: string,
  disabled?: boolean,
  opensInNewTab?: boolean
) => {
  return {
    to: disabled ? '' : absoluteUrl,
    target: opensInNewTab ? '_blank' : undefined,
  }
}

/**
 * Get the props for the component.
 * @param Component - The component type.
 * @param absoluteUrl - The absolute URL.
 * @param disabled - If true, the component will be disabled.
 * @param isLoading - If true, the component will be loading.
 * @param opensInNewTab - If true, the component will open in a new tab.
 * @returns The props for the component.
 */
export const getComponentProps = (
  Component: React.ElementType,
  type: ButtonTypeAttribute,
  absoluteUrl: string,
  disabled?: boolean,
  isLoading?: boolean,
  opensInNewTab?: boolean
) => {
  switch (Component) {
    case 'button':
      return getButtonProps(type, disabled, isLoading)
    case 'a':
      return getAnchorProps(absoluteUrl, disabled, opensInNewTab)
    default:
      return getLinkProps(absoluteUrl, disabled, opensInNewTab)
  }
}
