import { Selector } from 'testcafe'
import { ReactSelector, waitForReact } from 'testcafe-react-selectors'

fixture `SignupPage | Création d'un compte utilisateur`
    .page `http://localhost:3000/inscription`
    .beforeEach(async () => {
        await waitForReact()
    });

const nameInput = Selector('#input_users_publicName')
const emailInput = Selector('#input_users_email')
const passwordInput = Selector('#input_users_password')
const userContactOk = Selector('#input_users_contact_ok')
const signUpButton  = Selector('.is-primary')
const signInButton  = Selector('.is-secondary')

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {

  await t
  .click(signInButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test('Lorsque je remplis les champs et coche la checkbox, le bouton créer est activé', async t => {
    await t
    .typeText(nameInput, 'Public Name')
    .typeText(emailInput, 'email@email.test')
    .typeText(passwordInput, 'Pa$$word')
    .click(userContactOk)
    .expect(signInButton.visible).ok()
    .click(signUpButton)
})

test("lorsque le user est créé, l'utilisateur est redirigé vers la page /découverte", async t => {
  // si réponse api ok, j'ai un user et pas d'erreurs > redirect vers /decouverte gérér par le hoc _withSign

  // const SignupPage = ReactSelector('SignupPage')
  const SignupPage = ReactSelector('_withSign')
  // l'ajout de withProps, il aime pas...
  const component  = await SignupPage.getReact()
  console.log('----- button ---- ', component.props)
  await t.expect(component.props.match.path).eql('/inscription')
  await t.expect(component.props.user).eql(null)

})
