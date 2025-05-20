import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { RadioButton } from './RadioButton'

export default {
  title: 'design-system/RadioButton',
  decorators: [withRouter],
  component: RadioButton,
}

export const Default: StoryObj<typeof RadioButton> = {
  render: () => (
    <div style={{ display: 'flex', gap: 12 }}>
      <RadioButton name="gender_default" label="Homme" value="male" />
      <RadioButton name="gender_default" label="Femme" value="female" />
    </div>
  ),
}

export const Disabled: StoryObj<typeof RadioButton> = {
  render: () => (
    <div style={{ display: 'flex', gap: 12 }}>
      <RadioButton name="gender_disabled" label="Homme" value="male" disabled />
      <RadioButton
        name="gender_disabled"
        label="Femme"
        value="female"
        disabled
        checked
      />
    </div>
  ),
}
