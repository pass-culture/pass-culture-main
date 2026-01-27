import type { StoryObj } from '@storybook/react-vite'

import { ArtistSelect } from './ArtistSelect'

export default {
  title: '@/components/ArtistSelect',
  component: ArtistSelect,
}

export const Default: StoryObj<typeof ArtistSelect> = {
  args: {
    name: "artiste select",
    label: "Artistes :"
  },
}

