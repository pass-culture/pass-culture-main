import type { Meta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Button as ButtonComponent } from './Button'
import { ButtonColor, ButtonProps, ButtonSize, ButtonType, ButtonVariant, IconPositionEnum } from './types'
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
  argTypes: {
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
      defaultValue: false,
    },
    hovered: {
      control: 'boolean',
      defaultValue: false,
    },
    transparent: {
      control: 'boolean',
      defaultValue: false,
    },
    opensInNewTab: {
      control: 'boolean',
      defaultValue: false,
    },
    to: {
      control: 'text',
      defaultValue: '',
    },
    isExternal: {
      control: 'boolean',
      defaultValue: false,
    },
    isSectionLink: {
      control: 'boolean',
      defaultValue: false,
    },
  },
}

export default meta

const styles: React.CSSProperties = {
  alignItems: 'center',
  display: 'flex',
  flexDirection: 'row',
  gap: '12px',
} as React.CSSProperties

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
    color: ButtonColor.BRAND,
    variant: ButtonVariant.PRIMARY,
    label: 'Button Label',
    disabled: false,
    hovered: false,
    isLoading: false,
    size: ButtonSize.DEFAULT,
    type: ButtonType.BUTTON,
    icon: undefined,
    iconAlt: "",
    iconPosition: IconPositionEnum.LEFT,
    iconClassName: "",
    transparent: false,
    fullWidth: false,
    opensInNewTab: false,
    to: '',
    isExternal: false,
    isSectionLink: false,
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
      <Button label="Full Width" fullWidth={true} />
    </div>
  ),
}

/**
 * Story for the disabled button.
 */
export const ButtonDisabled: Story = {
  render: () => (
    <div style={styles}>
      <Button label="Disabled" disabled={true} />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled={true} />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled={true} />
    </div>
  ),
}

/**
 * Story for the loading button.
 */
export const ButtonLoading: Story = {
  render: () => (
    <div style={styles}>
      <Button label="Loading" isLoading={true} />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading={true} />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading={true} />
      <Button isLoading={true} icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
      <Button size={ButtonSize.SMALL} isLoading={true} icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
  ),
}

/**
 * Story for the transparent button.
 */
export const ButtonTransparent: Story = {
  render: () => (
    <div style={{ ...styles, backgroundColor: '#F2F2F2', padding: '10px' }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent={true} />
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
      <Button to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal={true} />
    </div>
  ),
}

/**
 * Story for the button with an external link and target _blank
 */
export const ButtonWithExternalLinkAndTargetBlank: Story = {
  render: () => (
    <div style={styles}>
      <Button to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal={true} opensInNewTab={true} />
    </div>
  ),
}

/**
 * Story for all button variants.
 */
export const ButtonVariants: Story = {
  render: () => (
    <>
    <div style={styles}>
      <div>
        <Button label="Primary" variant={ButtonVariant.PRIMARY} />
        <Button label="Secondary" variant={ButtonVariant.SECONDARY} />
        <Button label="Tertiary" variant={ButtonVariant.TERTIARY} />
      </div>
      <div>
        <Button label="Primary Hovered" hovered={true} variant={ButtonVariant.PRIMARY} />
        <Button label="Secondary Hovered" hovered={true} variant={ButtonVariant.SECONDARY} />
        <Button label="Tertiary Hovered" hovered={true} variant={ButtonVariant.TERTIARY} />
      </div>
      <div>
        <Button label="Primary Disabled" disabled={true} variant={ButtonVariant.PRIMARY} />
        <Button label="Secondary Disabled" disabled={true} variant={ButtonVariant.SECONDARY} />
        <Button label="Tertiary Disabled" disabled={true} variant={ButtonVariant.TERTIARY} />
      </div>
    </div>
    <div style={styles}>
    <div>
        <Button label="Secondary" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} />
        <Button label="Tertiary" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} />
      </div>
      <div>
        <Button label="Secondary Hovered" hovered={true} variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} />
        <Button label="Tertiary Hovered" hovered={true} variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} />
      </div>
      <div>
        <Button label="Secondary Disabled" disabled={true} variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} />
        <Button label="Tertiary Disabled" disabled={true} variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} />
      </div>
    </div>
    </>
  ),
}