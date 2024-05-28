import type { StoryObj } from '@storybook/react'

import { AdageButtonFilter } from './AdageButtonFilter'

export default {
  title: 'components/AdageButtonFilter',
  component: AdageButtonFilter,
}

export const AdageButton: StoryObj<typeof AdageButtonFilter> = {
  args: {
    title: 'Lieu de l’intervention',
    children: <div>lieu de l’intervention modal</div>,
    isActive: false,
    disabled: false,
  },
}
