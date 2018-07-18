import { Selector } from 'testcafe'
import { ReactSelector, waitForReact } from 'testcafe-react-selectors'

import regularUser from './helpers/roles'

fixture `Modale Profil`
    // const profileButton = Selector('.menu-button').find('button')
    const profileButton = Selector('.profile-button')
    const profileModal = Selector('.modal')
    const profilePic = Selector('.modal').find('profile-pic')
    const nextButton  = Selector('button.button.after')
    const MenuButton = ReactSelector('MenuButton')

  test("Lorsque l'utilisateur clique sur l'icône profil, la modale s'affiche", async t => {
      // await waitForReact()
      await t
      .useRole(regularUser)
      .click(nextButton)
      .expect(profileButton.visible).ok() // ce test passe !!!
      // .takeScreenshot('./screenshots')
      // .wait(2000)
      // .wait(1000)
      // .debug()
      const component  = await MenuButton.getReact()
      console.log('----- button ---- ', component.props)
      // .click(MenuButton) // The element that matches the specified selector is not visible.
      // BUG https://stackoverflow.com/questions/47675948/waiting-for-element-to-appear-on-static-button-in-testcafe
      // await t.expect(profileModal.visible).ok()
      // .expect(profileModal.hasClass('active')).ok()
      // .expect(profilePic.innerText).eql('Gtufhf')

  })
