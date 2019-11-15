import { selectTypeSublabels, selectTypeSublabelsAndDescription } from '../typesSelectors'
import state from '../../../mocks/state'

describe('selectTypeSublabels', () => {
  it('should select the global state', () => {
    expect(selectTypeSublabels(state)).toStrictEqual([
      'Applaudir',
      'Jouer',
      'Lire',
      'Pratiquer',
      'Regarder',
      'Rencontrer',
      'Écouter',
    ])
  })
})

describe('selectTypeSublabelsAndDescription', () => {
  it('should select the global state', () => {
    const expected = [
      {
        description:
          'Suivre un géant de 12 mètres dans la ville ? Rire aux éclats devant un stand up ? Rêver le temps d’un opéra ou d’un spectacle de danse ? Assister à une pièce de théâtre, ou se laisser conter une histoire ?',
        sublabel: 'Applaudir',
      },
      {
        description:
          'Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?',
        sublabel: 'Écouter',
      },
      {
        description:
          'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?',
        sublabel: 'Jouer',
      },
      {
        description:
          'S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?',
        sublabel: 'Lire',
      },
      {
        description:
          'Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?',
        sublabel: 'Pratiquer',
      },
      {
        description:
          'Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
        sublabel: 'Regarder',
      },
      {
        description: 'Parfois une simple rencontre peut changer une vie...',
        sublabel: 'Rencontrer',
      },
    ]
    expect(selectTypeSublabelsAndDescription(state)).toStrictEqual(expected)
  })
})
