import { Selector } from 'testcafe'

import BROWSER_ROOT_URL from './helpers/config'
import regularUser from './helpers/roles'

fixture `Modale Profil`
    const MenuButton = Selector('.menu-button').filterVisible()
    const rectoDivProfileButton = MenuButton.find('button.profile-button')

  test("Lorsque je clique sur l'icône profil, la modale s'affiche", async t => {
      await t
      .useRole(regularUser)
      .navigateTo(BROWSER_ROOT_URL+'decouverte/AH7Q/AU')
      .wait(1000)
      await t.expect(MenuButton.visible).ok() // ce test passe !!!
      await t.expect(rectoDivProfileButton.count).eql(2) // ce test passe !!!
      .click(rectoDivProfileButton.nth(1)) // The element that matches the specified selector is not visible.
      // BUG https://stackoverflow.com/questions/47675948/waiting-for-element-to-appear-on-static-button-in-testcafe
  })
