import React from 'react'

import testImg from './__specs__/offer_storie_image.jpg'

import { OfferAppPreview } from './'

const offerData = {
  name: 'Le mouton à trois pattes',
  description:
    "Avec un titre aussi mysterieu, il vous sera impossible de resiter à l'envie d'ouvrir ce merveilleux ouvrage.",
  isEvent: true,
  isDuo: true,
}

const venueData = {
  isVirtual: false,
  name: 'Nom du lieu',
  publicName: 'Nom public du lieu',
  address: '1 rue de la corniche',
  postalCode: '42021',
  city: 'Belegueuse',
  withdrawalDetails: "3em étoile à gauche et tout droit jusqu'au matin.",
}

export default {
  title: 'components/OfferAppPreview',
  component: OfferAppPreview,
}
const Template = args => <OfferAppPreview {...args} />

export const Default = Template.bind({})

Default.args = {
  imageSrc: testImg,
  offerData,
  venueData,
}

export const NoImage = Template.bind({})
NoImage.args = {
  imageSrc: undefined,
  offerData,
  venueData,
}

export const NotDuo = Template.bind({})
NotDuo.args = {
  imageSrc: testImg,
  offerData: {
    ...offerData,
    isDuo: false,
  },
  venueData,
}

export const TextTooLong = Template.bind({})
TextTooLong.args = {
  imageSrc: testImg,
  offerData: {
    ...offerData,
    name: `Les douze moutons, aux nombre de pattes variable voulant participer aux jeux olympique. Instant préérique ou la compétition bàààààhéé sont plein.
    Ce titre semble bien trop long pour apparaitre en entier sur cette prévisualisation, mais etonnament, c'est le comportement que nous avons actuelement. Voulons nous le changer ? Cela peut il faire débat, durant combient de temps ?
    La question est posé, l'avenir nous le dira.`,
    description: `Même si on se ment, après il faut s'intégrer tout ça dans les environnements et il faut se recréer... pour recréer... a better you et cela même si les gens ne le savent pas ! Mais ça, c'est uniquement lié au spirit.

    Même si on se ment, ce n'est pas un simple sport car c'est un très, très gros travail et c'est une sensation réelle qui se produit si on veut ! Et j'ai toujours grandi parmi les chiens.

    Oui alors écoute moi, même si on frime comme on appelle ça en France... il faut se recréer... pour recréer... a better you et c'est une sensation réelle qui se produit si on veut ! C'est pour ça que j'ai fait des films avec des replicants.`,
  },
  venueData: {
    ...venueData,
    withdrawalDetails: `Même si on se ment, après il faut s'intégrer tout ça dans les environnements et il faut se recréer... pour recréer... a better you et cela même si les gens ne le savent pas ! Mais ça, c'est uniquement lié au spirit.

    Même si on se ment, ce n'est pas un simple sport car c'est un très, très gros travail et c'est une sensation réelle qui se produit si on veut ! Et j'ai toujours grandi parmi les chiens.

    Oui alors écoute moi, même si on frime comme on appelle ça en France... il faut se recréer... pour recréer... a better you et c'est une sensation réelle qui se produit si on veut ! C'est pour ça que j'ai fait des films avec des replicants.`,
  },
}
