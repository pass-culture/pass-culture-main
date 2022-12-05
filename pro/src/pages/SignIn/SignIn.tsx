import PageTitle from 'components/PageTitle/PageTitle'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import Logo from 'ui-kit/Logo/Logo'

import SigninForm from './SigninForm/SigninForm'

const SignIn = (): JSX.Element => {
  useRedirectLoggedUser()

  return (
    <>
      <PageTitle title="Se connecter" />
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <section className="scrollable-content-side">
        <div className="content">
          <h1>Bienvenue sur l’espace dédié aux acteurs culturels</h1>
          <span className="has-text-grey">
            Tous les champs sont obligatoires
          </span>
          <SigninForm />
        </div>
      </section>
    </>
  )
}

export default SignIn
