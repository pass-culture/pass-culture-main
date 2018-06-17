export function collectionToPath (collectionName) {
  switch(collectionName) {
    case 'events':
      return 'evenements'
    case 'mediations':
      return 'accroches'
    case 'venues':
      return 'lieux';
    case 'offerers':
      return 'structures'
    case 'things':
      return 'objets'
    default:
      return collectionName
  }
}

export function pathToCollection (path) {
  switch(path) {
    case 'accroches':
      return 'mediations'
    case 'evenements':
      return 'events'
    case 'lieux':
      return 'venues'
    case 'objets':
      return 'things';
    case 'structures':
      return 'offerers'
    default:
      return path;
  }
}

export function pathToModel (path) {
  switch(path) {
    case 'evenements':
      return 'Event'
    case 'objets':
      return 'Thing';
    default:
      return path;
  }
}

export function modelToPath (model) {
  switch(model) {
    case 'Event':
      return 'evenements'
    case 'Thing':
      return 'lieux';
    default:
      return model;
  }
}

export function typeToTag (type) {
  switch (type) {
    case 'ComedyEvent':
      return 'Comédie'
    case 'DanceEvent':
      return 'Danse'
    case 'Festival':
      return 'Festival'
    case 'LiteraryEvent':
      return 'Lecture'
    case 'MusicEvent':
      return 'Musique'
    case 'ScreeningEvent':
      return 'Cinéma'
    case 'TheaterEvent':
      return 'Théâtre'
    default:
      return type
  }
}
