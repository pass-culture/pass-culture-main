import { Routes, Route } from 'react-router-dom-v5-compat'

import { SignupOffererFormLayout } from 'components/SignupOffererFormLayout'

const SignupOffererRoutes = () => {
  return (
    <SignupOffererFormLayout>
      <Routes>
        <Route path={'/signup/authentification'}>
          <div>Authentification</div>
        </Route>
        <Route path={'/signup/activite'}>
          <div>Activité</div>
        </Route>
        <Route path={'/signup/validation'}>
          <div>Validation</div>
        </Route>
      </Routes>
    </SignupOffererFormLayout>
  )
}

export default SignupOffererRoutes
