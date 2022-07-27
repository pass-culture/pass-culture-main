import { Story } from '@storybook/react'
import React, { ChangeEventHandler } from 'react'

import { ReactComponent as Icon } from 'icons/ico-calendar.svg'

import BaseCheckbox from './BaseCheckbox'

export default {
  title: 'ui-kit/forms/shared/BaseCheckbox',
  component: BaseCheckbox,
}

const Template: Story<{
  label: string
  hasError: boolean
  disabled: boolean
  onChange: ChangeEventHandler<HTMLInputElement>
  Icon: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}> = args => (
  <div>
    <BaseCheckbox {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  label: 'radio label',
  hasError: false,
  disabled: false,
  onChange: () => {},
  Icon,
}
