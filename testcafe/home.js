import { Selector } from 'testcafe'
import { BROWSER_URL } from '../src/utils/config'

fixture `Home`
  .page `${BROWSER_URL}`

test('logo', async t => {
    await t
      .expect(Selector('.header__logo').innerText)
      .eql('Pass Culture')
})
