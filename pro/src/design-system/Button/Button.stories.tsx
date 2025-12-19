import type { Meta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Button as ButtonComponent } from './Button'
import { ButtonColor, ButtonProps, ButtonSize, ButtonVariant, IconPositionEnum } from './types'
import { fullIcons } from '@/ui-kit/Icons/iconsList'
import fullNextIcon from '@/icons/full-next.svg'

const iconOptions = {
  none: null,
  ...Object.fromEntries(
    fullIcons.map((icon) => {
      // extract the name of the icon from the path (ex: '@/icons/full-link.svg' -> 'full-link')
      const name = icon.src.split('/').pop()?.replace('.svg', '') || ''
      return [name, icon.src]
    })
  ),
}

/**
 * Meta object for the Button component.
 */
const meta: Meta<typeof ButtonComponent> = {
  title: '@/design-system/Button',
  component: ButtonComponent,
  decorators: [withRouter],
  args: {
    as: 'button',
    color: ButtonColor.BRAND,
    variant: ButtonVariant.PRIMARY,
    size: ButtonSize.DEFAULT,
    label: '',
    disabled: false,
    hovered: false,
    isLoading: false,
    transparent: false,
    fullWidth: false,
    tooltip: '',
    icon: undefined,
    iconAlt: '',
    iconPosition: IconPositionEnum.LEFT,
    iconClassName: '',
  },
  argTypes: {
    as: {
      control: 'select',
      options: ['button', 'a'],
    },
    size: {
      control: 'select',
      options: Object.values(ButtonSize),
    },
    variant: {
      control: 'select',
      options: Object.values(ButtonVariant),
    },
    icon: {
      control: 'select',
      options: Object.keys(iconOptions),
      mapping: iconOptions,
    },
    iconPosition: {
      control: 'select',
      options: Object.values(IconPositionEnum),
    },
    color: {
      control: 'select',
      options: Object.values(ButtonColor),
    },
    disabled: {
      control: 'boolean',
    },
    hovered: {
      control: 'boolean',
    },
    isLoading: {
      control: 'boolean',
    },
    transparent: {
      control: 'boolean',
    },
    fullWidth: {
      control: 'boolean',
    },
    tooltip: {
      control: 'text',
    },
    // Props link
    to: {
      control: 'text',
      if: { arg: 'as', eq: 'a' },
    },
    opensInNewTab: {
      control: 'boolean',
      if: { arg: 'as', eq: 'a' },
    },
    isExternal: {
      control: 'boolean',
      if: { arg: 'as', eq: 'a' },
    },
    isSectionLink: {
      control: 'boolean',
      if: { arg: 'as', eq: 'a' },
    },
  },
}

export default meta

const styles: React.CSSProperties = {
  alignItems: 'center',
  display: 'flex',
  flexDirection: 'row',
  gap: '12px',
}

/**
 * Story type for the Button component.
 */
type Story = StoryObj<typeof ButtonComponent>

const Button = (args: ButtonProps) => {
  return <ButtonComponent {...args} />
}

/**
 * Story for the default Button component.
 */
export const DefaultButton: Story = {
  render: (args: ButtonProps) => <Button {...args} />,
  args: {
    label: 'Button Label',
  },
}

/**
 * Story for the default button variants.
 */
export const DefaultButtonVariants: Story = {
  render: () => (
    <div style={styles}>
      <Button label="Primary" />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary" />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary" />
    </div>
  ),
}

/**
 * Story for the neutral button variants.
 */
export const NeutralButtonVariants: Story = {
  render: () => (
    <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Neutral' color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Neutral" color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Neutral" color={ButtonColor.NEUTRAL} />
    </div>
  ),
}

/**
 * Story for the button sizes
 */
export const ButtonSizes: Story = {
  render: () => (
    <div style={styles}>
      <Button size={ButtonSize.SMALL} label="Small" variant={ButtonVariant.PRIMARY} />
      <Button label="Default" variant={ButtonVariant.PRIMARY} />
    </div>
  ),
}

/**
 * Story for the icons with large size
 */
export const ButtonIconsLarge: Story = {
  render: () => (
    <div style={styles}>
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
  ),
}

/**
 * Story for the icons with small size
 */
export const ButtonIconsSmall: Story = {
  render: () => (
    <div style={styles}>
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
  ),
}

/**
 * Story for the full width button, the button will take the full width of the container (for example, max width 400px)
 */
export const ButtonFullWidth: Story = {
  render: () => (
    <div style={{ ...styles, maxWidth: '400px' }}>
      <Button label="Full Width" fullWidth />
    </div>
  ),
}

/**
 * Story for the disabled button.
 */
export const ButtonDisabled: Story = {
  render: () => (
    <div style={styles}>
      <Button label="Disabled" disabled />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled />
    </div>
  ),
}

/**
 * Story for the loading button.
 */
export const ButtonLoading: Story = {
  render: () => (
    <div style={styles}>
      <Button label="Loading" isLoading />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading />
      <Button isLoading icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
      <Button size={ButtonSize.SMALL} isLoading icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
  ),
}

/**
 * Story for the button with a tooltip.
 */
export const ButtonTooltip: Story = {
  render: () => (
    <div style={styles}>
      <Button tooltip="Tooltip text" icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
      <Button tooltip="Tooltip text" icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} disabled />
    </div>
  ),
}

/**
 * Story for the transparent button.
 */
export const ButtonTransparent: Story = {
  render: () => (
    <div style={{ ...styles, backgroundColor: '#F2F2F2', padding: '10px' }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent />
      <Button label="Not Transparent" variant={ButtonVariant.SECONDARY} transparent={false} />
    </div>
  ),
}

/**
 * Story for the button with an external link (uses <a> tag)
 */
export const ButtonWithExternalLink: Story = {
  render: () => (
    <div style={styles}>
      <Button as='a' to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal />
    </div>
  ),
}

/**
 * Story for the button with an external link and target _blank
 */
export const ButtonWithExternalLinkAndTargetBlank: Story = {
  render: () => (
    <div style={styles}>
      <Button as="a" to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal opensInNewTab />
    </div>
  ),
}

const columnStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  marginBottom: 24
}

const titleStyles: React.CSSProperties = {
  marginBottom: 16
}

/**
 * Story for all button variants.
 */
export const ButtonVariants: Story = {
  render: () => (
    <>
      <div>
      <h2 style={titleStyles}>Brand</h2>
        <div style={columnStyles}>
          <Button label="Primary" variant={ButtonVariant.PRIMARY} />
          <Button label="Primary Hovered" variant={ButtonVariant.PRIMARY} hovered />
          <Button label="Tertiary Disabled" variant={ButtonVariant.TERTIARY} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Secondary" variant={ButtonVariant.SECONDARY} />
          <Button label="Secondary Hovered" variant={ButtonVariant.SECONDARY} hovered />
          <Button label="Secondary Disabled" variant={ButtonVariant.SECONDARY} disabled />
          
        </div>
        <div style={columnStyles}>
          <Button label="Tertiary" variant={ButtonVariant.TERTIARY} />
          <Button label="Tertiary Hovered" variant={ButtonVariant.TERTIARY} hovered />
          <Button label="Primary Disabled" variant={ButtonVariant.PRIMARY} disabled />
        </div>
      </div>
      <div style={{marginTop: 24}}>
        <h2 style={titleStyles}>Neutral</h2>
        <div style={columnStyles}>
          <Button label="Primary" variant={ButtonVariant.PRIMARY} color={ButtonColor.NEUTRAL} />
          <Button label="Primary Hovered" variant={ButtonVariant.PRIMARY} color={ButtonColor.NEUTRAL} hovered />
          <Button label="Primary Disabled" variant={ButtonVariant.PRIMARY} color={ButtonColor.NEUTRAL} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Secondary" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} />
          <Button label="Secondary Hovered" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} hovered />
          <Button label="Secondary Disabled" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Tertiary" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} />
          <Button label="Tertiary Hovered" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} hovered />
          <Button label="Tertiary Disabled" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} disabled />
        </div>
      </div>
    </>
  ),
}