import { Selector } from 'testcafe'
import { validatedOffererUserRole } from './helpers/roles'

async function trimed(selector, lol) {
  return await selector.innerText.then(value => value.trim())
}

const offerListLink = Selector('.navbar-item').withText('Vos offres')
const offerActivSwitch = Selector('.offer-item .activ-switch')
const offerActivSwitchText = () => trimed(Selector('.offer-item .activ-switch'))

fixture`061_01 OfferList | Lister les offres`

test("Lorsque je cliques sur `Mes offres`, j'accès de à la liste des offres", async t => {
  await t.useRole(validatedOffererUserRole).click(offerListLink)

  const location = await t.eval(() => window.location)
  let value

  await t.expect(location.pathname).eql('/offres')

  await t
    .expect(await offerActivSwitchText())
    .eql('Désactiver')
    .click(offerActivSwitch)

  await t
    .expect(await offerActivSwitchText())
    .eql('Activer')
    .click(offerActivSwitch)

  await t.expect(await offerActivSwitchText()).eql('Désactiver')
})
