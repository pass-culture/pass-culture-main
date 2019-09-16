const offerTypes = [
  {
    description:
      'Action, science-fiction, documentaire ou com\u00e9die sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c\u2019\u00e9tait plut\u00f4t cette exposition qui allait faire son cin\u00e9ma ?',
    label: 'Cin\u00e9ma (Projections, S\u00e9ances, \u00c9v\u00e8nements)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Regarder',
    type: 'Event',
    value: 'EventType.CINEMA',
    isActive: true,
  },
  {
    description: 'Parfois une simple rencontre peut changer une vie...',
    label: 'Conf\u00e9rence \u2014 D\u00e9bat \u2014 D\u00e9dicace',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Rencontrer',
    type: 'Event',
    value: 'EventType.CONFERENCE_DEBAT_DEDICACE',
    isActive: true,
  },
  {
    description:
      'R\u00e9soudre l\u2019\u00e9nigme d\u2019un jeu de piste dans votre ville ? Jouer en ligne entre amis ? D\u00e9couvrir cet univers \u00e9trange avec une manette ?',
    label: 'Jeux (\u00c9venements, Rencontres, Concours)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Jouer',
    type: 'Event',
    value: 'EventType.JEUX',
    isActive: true,
  },
  {
    description:
      'Plut\u00f4t rock, rap ou classique ? Sur un smartphone avec des \u00e9couteurs ou entre amis au concert ?',
    label: 'Musique (Concerts, Festivals)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: '\u00c9couter',
    type: 'Event',
    value: 'EventType.MUSIQUE',
    isActive: true,
  },
  {
    description:
      'Action, science-fiction, documentaire ou com\u00e9die sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c\u2019\u00e9tait plut\u00f4t cette exposition qui allait faire son cin\u00e9ma ?',
    label:
      'Mus\u00e9es \u2014 Patrimoine (Expositions, Visites guid\u00e9es, Activit\u00e9s sp\u00e9cifiques)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Regarder',
    type: 'Event',
    value: 'EventType.MUSEES_PATRIMOINE',
    isActive: true,
  },
  {
    description:
      'Jamais os\u00e9 monter sur les planches ? Tenter d\u2019apprendre la guitare, le piano ou la photographie ? Partir cinq jours d\u00e9couvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?',
    label: 'Pratique Artistique (Stages ponctuels)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Pratiquer',
    type: 'Event',
    value: 'EventType.PRATIQUE_ARTISTIQUE',
    isActive: true,
  },
  {
    description:
      'Suivre un g\u00e9ant de 12 m\u00e8tres dans la ville ? Rire aux \u00e9clats devant un stand up ? R\u00eaver le temps d\u2019un op\u00e9ra ou d\u2019un spectacle de danse ? Assister \u00e0 une pi\u00e8ce de th\u00e9\u00e2tre, ou se laisser conter une histoire ?',
    label: 'Spectacle vivant',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Applaudir',
    type: 'Event',
    value: 'EventType.SPECTACLE_VIVANT',
    isActive: true,
  },
  {
    description:
      'Action, science-fiction, documentaire ou com\u00e9die sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c\u2019\u00e9tait plut\u00f4t cette exposition qui allait faire son cin\u00e9ma ?',
    label: 'Audiovisuel (Films sur supports physiques et VOD)',
    offlineOnly: false,
    onlineOnly: false,
    sublabel: 'Regarder',
    type: 'Thing',
    value: 'ThingType.AUDIOVISUEL',
    isActive: true,
  },
  {
    description:
      'Action, science-fiction, documentaire ou com\u00e9die sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c\u2019\u00e9tait plut\u00f4t cette exposition qui allait faire son cin\u00e9ma ?',
    label: 'Cin\u00e9ma (Abonnements)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Regarder',
    type: 'Thing',
    value: 'ThingType.CINEMA_ABO',
    isActive: true,
  },
  {
    description:
      'R\u00e9soudre l\u2019\u00e9nigme d\u2019un jeu de piste dans votre ville ? Jouer en ligne entre amis ? D\u00e9couvrir cet univers \u00e9trange avec une manette ?',
    label: 'Jeux (Abonnements)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Jouer',
    type: 'Thing',
    value: 'ThingType.JEUX_ABO',
    isActive: true,
  },
  {
    description:
      'R\u00e9soudre l\u2019\u00e9nigme d\u2019un jeu de piste dans votre ville ? Jouer en ligne entre amis ? D\u00e9couvrir cet univers \u00e9trange avec une manette ?',
    label: 'Jeux Vid\u00e9o',
    offlineOnly: false,
    onlineOnly: true,
    sublabel: 'Jouer',
    type: 'Thing',
    value: 'ThingType.JEUX_VIDEO',
    isActive: true,
  },
  {
    description:
      'S\u2019abonner \u00e0 un quotidien d\u2019actualit\u00e9 ? \u00c0 un hebdomadaire humoristique ? \u00c0 un mensuel d\u00e9di\u00e9 \u00e0 la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?',
    label: 'Livre \u2014 \u00c9dition',
    offlineOnly: false,
    onlineOnly: false,
    sublabel: 'Lire',
    type: 'Thing',
    value: 'ThingType.LIVRE_EDITION',
    isActive: true,
  },
  {
    description:
      'Action, science-fiction, documentaire ou com\u00e9die sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c\u2019\u00e9tait plut\u00f4t cette exposition qui allait faire son cin\u00e9ma ?',
    label: 'Mus\u00e9es \u2014 Patrimoine (Abonnements, Visites libres)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Regarder',
    type: 'Thing',
    value: 'ThingType.MUSEES_PATRIMOINE_ABO',
    isActive: true,
  },
  {
    description:
      'Plut\u00f4t rock, rap ou classique ? Sur un smartphone avec des \u00e9couteurs ou entre amis au concert ?',
    label: 'Musique (Abonnements concerts)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: '\u00c9couter',
    type: 'Thing',
    value: 'ThingType.MUSIQUE_ABO',
    isActive: true,
  },
  {
    description:
      'Plut\u00f4t rock, rap ou classique ? Sur un smartphone avec des \u00e9couteurs ou entre amis au concert ?',
    label: 'Musique (sur supports physiques ou en ligne)',
    offlineOnly: false,
    onlineOnly: false,
    sublabel: '\u00c9couter',
    type: 'Thing',
    value: 'ThingType.MUSIQUE',
    isActive: true,
  },
  {
    description:
      'Jamais os\u00e9 monter sur les planches ? Tenter d\u2019apprendre la guitare, le piano ou la photographie ? Partir cinq jours d\u00e9couvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?',
    label: 'Pratique Artistique (Abonnements)',
    offlineOnly: true,
    onlineOnly: false,
    sublabel: 'Pratiquer',
    type: 'Thing',
    value: 'ThingType.PRATIQUE_ARTISTIQUE_ABO',
    isActive: true,
  },
  {
    description:
      'S\u2019abonner \u00e0 un quotidien d\u2019actualit\u00e9 ? \u00c0 un hebdomadaire humoristique ? \u00c0 un mensuel d\u00e9di\u00e9 \u00e0 la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?',
    label: 'Presse (Abonnements)',
    offlineOnly: false,
    onlineOnly: true,
    sublabel: 'Lire',
    type: 'Thing',
    value: 'ThingType.PRESSE_ABO',
    isActive: true,
  },
]

export default offerTypes
