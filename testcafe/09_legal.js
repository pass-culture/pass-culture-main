// ./node_modules/.bin/testcafe chrome:headless ./testcafe/09_legal.js
import { Selector } from 'testcafe'

import { version } from '../package.json'
import { ROOT_PATH } from '../src/utils/config'

fixture('09_01 Page Mentions Légales').beforeEach(async t => {
  await t.navigateTo(`${ROOT_PATH}mentions-legales`)
})

// Je vois le titre de la page dans le header
// J'ai un footer
// J'ai un titre dans une div main

test("Je peux cliquer sur l'icône menu qui se trouve en bas de page", async t => {
  const selector = Selector('#open-menu-button')
  await t
    .expect(selector.exists)
    .ok()
    .click(selector)
})

test("Le numero de version de l'app est affiché en bas de page", async t => {
  const selector = Selector('#terms-page-appversion')
  await t
    .expect(selector.exists)
    .ok()
    .expect(selector.innerText)
    .eql(`Pass Culture v.${version}`)
})

// Lorsque je clique sur la flêche retour j'arrive sur la page http://localhost:3000/decouverte/tuto/AE
