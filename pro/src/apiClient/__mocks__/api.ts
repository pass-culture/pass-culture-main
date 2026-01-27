import type { AdresseData } from '../adresse/types'
import type { ArtistsResponseModel } from '../v1'

const getArtists = async (
  searchText: string
): Promise<ArtistsResponseModel> => {
  await new Promise((resolve) => setTimeout(resolve, 500))
  return [
    {
      id: '1',
      name: 'Mimie Mathy',
      thumbUrl:
        'https://fr.wikipedia.org/wiki/Mimie_Mathy#/media/Fichier:Mimie_Mathy_Cannes.jpg',
    },
    {
      id: '2',
      name: 'Daft Punk',
      thumbUrl:
        'https://upload.wikimedia.org/wikipedia/commons/8/83/Daft_Punk_in_2013_2.jpg',
    },
    {
      id: '3',
      name: 'Justice',
      thumbUrl:
        'https://fr.wikipedia.org/wiki/Justice_(groupe)#/media/Fichier:Justice_(band).jpg',
    },
    { id: '4', name: 'Odezenne', thumbUrl: '' },
    { id: '5', name: 'Omaks', thumbUrl: '' },
    { id: '6', name: 'Téléphone', thumbUrl: '' },
    { id: '7', name: 'The Beatles', thumbUrl: '' },
  ].filter((artist) =>
    artist.name.toLowerCase().includes(searchText.toLowerCase())
  )
}

const getDataFromAddress = async (
  address: string
): Promise<Array<AdresseData>> => {
  await new Promise((resolve) => setTimeout(resolve, 500))
  return [
    {
      city: 'Paris',
      postalCode: '75001',
      address: address,
      inseeCode: 'ABC',
      id: 'abc',
      label: 'Mon adresse',
      latitude: 123,
      longitude: 456,
    },
  ]
}

export { getArtists, getDataFromAddress }

export const api = {
  getArtists,
  getDataFromAddress,
}
