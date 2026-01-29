import type { StoryObj } from '@storybook/react-vite'

import { ApiSelect, ApiOption } from './ApiSelect'

export default {
  title: '@/ui-kit/forms/ApiSelect',
  component: ApiSelect,
}

const searchApi = async (
  searchText: string
): Promise<ApiOption[]> => {
  await new Promise((resolve) => setTimeout(resolve, 500))
  return [
    {
      value: '1',
      label: 'Mimie Mathy',
      thumbUrl:
        'https://fr.wikipedia.org/wiki/Mimie_Mathy#/media/Fichier:Mimie_Mathy_Cannes.jpg',
    },
    {
      value: '2',
      label: 'Daft Punk',
      thumbUrl:
        'https://upload.wikimedia.org/wikipedia/commons/8/83/Daft_Punk_in_2013_2.jpg',
    },
    {
      value: '3',
      label: 'Justice',
      thumbUrl:
        'https://fr.wikipedia.org/wiki/Justice_(groupe)#/media/Fichier:Justice_(band).jpg',
    },
    { value: '4', label: 'Odezenne', thumbUrl: '' },
    { value: '5', label: 'Omaks', thumbUrl: '' },
    { value: '6', label: 'Téléphone', thumbUrl: '' },
    { value: '7', label: 'The Beatles', thumbUrl: '' },
  ]
}


export const Default: StoryObj<typeof ApiSelect> = {
  args: {
    name: "artist-select",
    label: "ApiSelect :",
    description: "Essayez The Beatles ou Daft Punk",
    searchApi: searchApi,
    minSearchLength: 1
  },
}

