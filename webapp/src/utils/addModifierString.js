const MODIFIER_STRING_ID = 'selectBookables'

/* ajoute une 'id' dans l'objet pour indiquer
le selecteur qui a modifié les objets utilisables par une vue */
export const addModifierString = () => items =>
  items.map(obj => ({
    ...obj,
    __modifiers__: (obj.__modifiers__ || []).concat([MODIFIER_STRING_ID]),
  }))
