export const searchedResults = {
  hits: [
    {
      _geoloc: {
        lat: 42.1,
        lng: 41.1
      },
      offer: {
        author: 'Emile Zola',
        dateRange: [
          '2019-12-11T20:00:00Z',
          '2019-12-26T21:00:00Z'
        ],
        description: 'L\'assommoir',
        id: 'VA',
        label: 'Livre - adolescent',
        name: 'L\'assommoir',
        type: 'Thingtype.LIVRE',
        thumbUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Oryctolagus_cuniculus_Tasmania_2.jpg/290px-Oryctolagus_cuniculus_Tasmania_2.jpg'
      },
      offerer: {
        name: 'Hall du livre',
        publicName: 'Hall du livre avec un nom de substitution',
      },
      venue: {
        city: 'Paris',
        name: 'Librairie du marais',
        publicName: 'Librairie du marais avec un nom de substitution',
      },
      objectID: 'BE2'
    },
    {
      _geoloc: {
        lat: 40.1,
        lng: 45.1
      },
      offer: {
        author: 'Guy de Maupassant',
        dateRange: [
          '2019-12-11T20:00:00Z',
          '2019-12-26T21:00:00Z'
        ],
        description: 'Boule de suif',
        id: 'TE',
        label: 'Livre - adolescent',
        name: 'Boule de suif',
        type: 'Thingtype.LIVRE',
        thumbUrl: 'https://monde.ccdmd.qc.ca/media/image1024/80557.jpg'
      },
      offerer: {
        name: 'Hall du livre',
        publicName: 'Hall du livre avec un nom de substitution',
      },
      venue: {
        city: 'Paris',
        name: 'Librairie du marais',
        publicName: 'Librairie du marais avec un nom de substitution',
      },
      objectID: 'BE3'
    },
  ],
  page: 0,
  nbHits: 2,
  nbPages: 1,
  hitsPerPage: 2,
  processingTimeMS: 1,
  query: "librairie",
  params: "query=librairie&hitsPerPage=2"
}
