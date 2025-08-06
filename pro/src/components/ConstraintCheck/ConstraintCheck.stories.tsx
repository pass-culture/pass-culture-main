import type { StoryObj } from '@storybook/react'

import { ConstraintCheck } from './ConstraintCheck'
import { imageConstraints } from './imageConstraints'

export default {
  title: '@/components/ConstraintCheck',
  component: ConstraintCheck,
}

export const Default: StoryObj<typeof ConstraintCheck> = {
  args: {
    constraints: [
      imageConstraints.formats(['image/png', 'image/jpeg']),
      imageConstraints.size(2_000_000),
      imageConstraints.width(300),
    ],
    failingConstraints: [],
  },
}

export const Failing: StoryObj<typeof ConstraintCheck> = {
  args: {
    constraints: [
      imageConstraints.formats(['image/png', 'image/jpeg']),
      imageConstraints.size(2_000_000),
      imageConstraints.width(300),
    ],
    failingConstraints: ['size', 'width'],
  },
}
