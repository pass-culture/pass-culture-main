import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

const menuButton = Selector('#open-menu-button')

fixture('09_01 Page Mentions Légales').beforeEach(async t => {
  await t.navigateTo(`${ROOT_PATH}mentions-legales`)
})

// Je vois le titre de la page dans le header
// J'ai un footer
// J'ai un titre dans une div main

test("Je peux cliquer sur l'icône menu qui se trouve en bas de page", async t => {
  await t.click(menuButton)
})

// Lorsque je clique sur la flêche retour j'arrive sur la page http://localhost:3000/decouverte/tuto/AE

// Je peux voir le numéro de version de l'app Pass Culture version v0.4.0
