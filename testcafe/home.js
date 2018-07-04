import { Selector } from 'testcafe'

fixture `BetaPage | Arrivée d'un nouvel utilisateur à la racine de la webapp`
    .page `http://localhost:3000/`

test('I should be redirected to beta pathname in first step', async t => {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/beta')
})

test('button Link to /inscription should redirect to /inscription when clicked', async t => {
    await t
      .expect(Selector('.button').innerText)
      .eql('C\'est par là')
      .click('.button')
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/inscription')
})
