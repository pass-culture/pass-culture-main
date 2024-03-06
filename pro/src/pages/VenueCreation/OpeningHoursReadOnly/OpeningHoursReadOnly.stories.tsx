import { StoryObj } from '@storybook/react'

import { OpeningHoursReadOnly } from './OpeningHoursReadOnly'

export default {
  title: 'components/OpeningHoursReadOnly',
  component: OpeningHoursReadOnly,
}

const openingHours = [
  { MONDAY: [{ open: '14:00', close: '19:30' }] },
  {
    TUESDAY: [
      { open: '10:00', close: '13:00' },
      { open: '14:00', close: '19:30' },
    ],
  },
  {
    WEDNESDAY: [
      { open: '10:00', close: '13:00' },
      { open: '14:00', close: '19:30' },
    ],
  },
  {
    THURSDAY: [
      { open: '10:00', close: '13:00' },
      { open: '14:00', close: '19:30' },
    ],
  },
  {
    FRIDAY: [
      { open: '10:00', close: '13:00' },
      { open: '14:00', close: '19:30' },
    ],
  },
  {
    SATURDAY: [
      { open: '10:00', close: '13:00' },
      { open: '14:00', close: '19:30' },
    ],
  },
  { SUNDAY: null },
]
export const Default: StoryObj<typeof OpeningHoursReadOnly> = {
  args: { openingHours },
}
