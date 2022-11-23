import type { Story } from '@storybook/react'
import React from 'react'

import Tag, { ITagProps } from './Tag'

export default {
  title: 'ui-kit/Tag',
  component: Tag,
}

const Template: Story<ITagProps> = args => <Tag {...args}></Tag>

export const Default = Template.bind({})

Default.args = {
  label: 'Offre collective',
}

export const Closeable = Template.bind({})

Closeable.args = {
  label: 'Offre collective',
  closeable: {
    onClose: () => {},
    closeLabel: 'Supprimer le tag',
  },
}
