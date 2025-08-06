import { StoryObj } from '@storybook/react'

import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import testImg from './__specs__/offer_storie_image.jpg'
import { OfferAppPreview } from './OfferAppPreview'

const baseOfferData = {
  name: 'Le mouton à trois pattes',
  description:
    "Avec un titre aussi mysterieux, il vous sera impossible de résister à l’envie d'ouvrir ce merveilleux ouvrage.",
  isEvent: true,
  isDuo: true,
  image: { url: testImg, originalUrl: testImg, credit: 'test' },
}

export default {
  title: '@/components/OfferAppPreview',
  component: OfferAppPreview,
}

export const Default: StoryObj<typeof OfferAppPreview> = {
  args: {
    offer: getIndividualOfferFactory(baseOfferData),
  },
}

export const NoImage: StoryObj<typeof OfferAppPreview> = {
  args: {
    offer: getIndividualOfferFactory({ ...baseOfferData }),
  },
}

export const NotDuo: StoryObj<typeof OfferAppPreview> = {
  args: {
    offer: getIndividualOfferFactory({ ...baseOfferData, isDuo: false }),
  },
}

export const TextTooLong: StoryObj<typeof OfferAppPreview> = {
  args: {
    offer: getIndividualOfferFactory({
      ...baseOfferData,
      name: `Les douze moutons, aux nombre de pattes variable voulant participer aux jeux olympique. Instant préérique ou la compétition bàààààhéé sont plein.
    Ce titre semble bien trop long pour apparaitre en entier sur cette prévisualisation, mais etonnament, c'est le comportement que nous avons actuelement. Voulons nous le changer ? Cela peut il faire débat, durant combient de temps ?
    La question est posé, l’avenir nous le dira.`,
      description: `Même si on se ment, après il faut s'intégrer tout ça dans les environnements et il faut se recréer... pour recréer... a better you et cela même si les gens ne le savent pas ! Mais ça, c'est uniquement lié au spirit.

    Même si on se ment, ce n’est pas un simple sport car c'est un très, très gros travail et c'est une sensation réelle qui se produit si on veut ! Et j'ai toujours grandi parmi les chiens.

    Oui alors écoute moi, même si on frime comme on appelle ça en France... il faut se recréer... pour recréer... a better you et c'est une sensation réelle qui se produit si on veut ! C'est pour ça que j'ai fait des films avec des replicants.`,
      withdrawalDetails: `Même si on se ment, après il faut s'intégrer tout ça dans les environnements et il faut se recréer... pour recréer... a better you et cela même si les gens ne le savent pas ! Mais ça, c'est uniquement lié au spirit.

    Même si on se ment, ce n’est pas un simple sport car c'est un très, très gros travail et c'est une sensation réelle qui se produit si on veut ! Et j'ai toujours grandi parmi les chiens.

    Oui alors écoute moi, même si on frime comme on appelle ça en France... il faut se recréer... pour recréer... a better you et c'est une sensation réelle qui se produit si on veut ! C'est pour ça que j'ai fait des films avec des replicants.`,
    }),
  },
}
