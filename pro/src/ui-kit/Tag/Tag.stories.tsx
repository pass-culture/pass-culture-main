import { StoryObj } from '@storybook/react'

import { Tag, TagVariant } from './Tag'

export default {
  title: 'ui-kit/Tag',
  component: Tag,
}

export const Default: StoryObj<typeof Tag> = {
  args: {
    children: 'Offre collective',
    variant: TagVariant.SMALL_OUTLINE,
  },
}
