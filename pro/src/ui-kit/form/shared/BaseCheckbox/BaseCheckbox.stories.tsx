import BaseCheckbox from './BaseCheckbox'
import { ReactComponent as Icon } from 'icons/ico-calendar.svg'
import React from 'react'
import { Story } from '@storybook/react'

export default {
  title: 'ui-kit/forms/shared/BaseCheckbox',
  component: BaseCheckbox,
}

const Template: Story<{
  label: string
  hasError: boolean
  disabled: boolean
  checked: boolean
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
  checked: false,
  Icon,
}
