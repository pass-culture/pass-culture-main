import { Link } from 'react-router'

import type { ButtonProps, ButtonTypeAttribute } from '../types'

export const getComponentType = ({
  as,
  disabled,
  isExternal,
  isSectionLink,
}: {
  as: 'button' | 'a'
  disabled?: boolean
  isExternal: boolean
  isSectionLink: boolean
}): React.ElementType => {
  if (as === 'button') {
    return 'button'
  }
  // A disabled <Link> is treated as an <a> to remove its `href` and inherit proper a11y from `getAnchorProps`.
  if (isExternal || isSectionLink || disabled) {
    return 'a'
  }

  return Link
}

export const getButtonProps = ({
  disabled,
  isLoading,
  onClick,
  type,
}: {
  disabled?: boolean
  isLoading?: boolean
  onClick?: ButtonProps['onClick']
  type: ButtonTypeAttribute
}) => {
  return {
    type,
    disabled: disabled || isLoading,
    onClick: disabled ? undefined : onClick,
  }
}

export const getAnchorProps = ({
  absoluteUrl,
  disabled,
  onClick,
  opensInNewTab,
}: {
  absoluteUrl: string
  disabled?: boolean
  onClick?: ButtonProps['onClick']
  opensInNewTab?: boolean
}) => {
  return {
    'aria-disabled': disabled || undefined,
    href: disabled ? undefined : absoluteUrl,
    onClick: disabled ? undefined : onClick,
    rel: 'noopener noreferrer',
    // No `href` => `role="generic"` => `role="link"` adjustment to help screen readers interpretation.
    // https://w3c.github.io/html-aria/#el-a
    role: disabled ? 'link' : undefined,
    target: opensInNewTab ? '_blank' : undefined,
  }
}

export const getLinkProps = ({
  absoluteUrl,
  disabled,
  onClick,
  opensInNewTab,
}: {
  absoluteUrl: string
  disabled?: boolean
  onClick?: ButtonProps['onClick']
  opensInNewTab?: boolean
}) => {
  return {
    onClick: disabled ? undefined : onClick,
    to: disabled ? '' : absoluteUrl,
    target: opensInNewTab ? '_blank' : undefined,
  }
}

export const getComponentProps = ({
  Component,
  type,
  absoluteUrl,
  disabled,
  isLoading,
  onClick,
  opensInNewTab,
}: {
  Component: React.ElementType
  type: ButtonTypeAttribute
  absoluteUrl: string
  disabled?: boolean
  isLoading?: boolean
  onClick?: ButtonProps['onClick']
  opensInNewTab?: boolean
}) => {
  switch (Component) {
    case 'button':
      return getButtonProps({ type, disabled, isLoading, onClick })
    case 'a':
      return getAnchorProps({ absoluteUrl, disabled, onClick, opensInNewTab })
    default:
      return getLinkProps({ absoluteUrl, disabled, onClick, opensInNewTab })
  }
}
