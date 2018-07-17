import { Selector } from 'testcafe'

fixture `BetaPage | Arrivée d'un nouvel utilisateur à la racine de la webapp`
    .page `http://localhost:3000/`

test('Le nouvel utilisateur est redirigé vers /beta', async t => {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/beta')
})

test("Lorsque le nouvel utilisateur clique sur le bouton, il est redirigé vers la page /inscription", async t => {
    await t
      .expect(Selector('.button').innerText)
      .eql('C\'est par là')
      .click('.button')
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/inscription')
})
