// NOTE: le filter pour supprimer les éléments `null`
// augmente les tests unitaires de 3s
import React from 'react'
import { Redirect } from 'react-router-dom'

import ActivationRoutesContainer from '../pages/activation/ActivationRoutesContainer'
import BetaPage from '../pages/BetaPage'
import MyBookingsPage from '../pages/my-bookings'
import DiscoveryPage from '../pages/discovery'
import FavoritesPage from '../pages/FavoritesPage'
import ForgotPasswordPage from '../pages/ForgotPasswordPage'
import ProfilePage from '../pages/profile'
import TypeFormPage from '../pages/typeform/TypeFormContainer'
import SearchContainer from '../pages/search/SearchContainer'
import SigninContainer from '../pages/signin/SigninContainer'
import SignupContainer from '../pages/signup/SignupContainer'
import { WEBAPP_CONTACT_EXTERNAL_PAGE } from '../../utils/config'
import { pipe } from '../../utils/functionnals'

export const removeHrefRoutes = routes =>
  routes.filter(route => !route.href)

export const removeDisabledRoutes = routes =>
  routes.filter(route => !route.disabled)

export const extendRoutesWithExact = routes =>
  routes.map(obj => {
    const exact = obj && obj.exact === undefined ? true : obj.exact
    const extend = { exact }
    return { ...obj, ...extend }
  })

export const addMenuViewToRoutesWithPath = routes =>
  routes.map(route => {
    const clone = { ...route }
    if (clone.path) {
      clone.path = `${clone.path}/:menu(menu)?`
    }
    return clone
  })

export const createIsFeatureDisabled = features => featureName =>
  features && features.every(feature =>
    feature.name !== featureName ||
    !feature.isActive
  )

export const getFeaturedRoutes = features => {
  const isFeatureDisabled = createIsFeatureDisabled(features)
  const featuredRoutes = [
    {
      path: '/',
      render: () => <Redirect to="/beta" />,
    },
    {
      component: BetaPage,
      path: '/beta',
      title: "Bienvenue dans l'avant-première du Pass Culture",
    },
    {
      component: ActivationRoutesContainer,
      path: '/activation/:token?',
      title: 'Activation',
    },
    {
      component: SigninContainer,
      path: '/connexion',
      title: 'Connexion',
    },
    {
      component: SignupContainer,
      disabled: isFeatureDisabled('WEBAPP_SIGNUP'),
      path: '/inscription',
      title: 'Inscription',
    },
    {
      component: ForgotPasswordPage,
      path: '/mot-de-passe-perdu/:view?',
      title: 'Mot de passe perdu',
    },
    {
      component: TypeFormPage,
      path: '/typeform',
      title: 'Questionnaire',
    },
    /* ---------------------------------------------------
     *
     * MENU ITEMS
     * NOTE les elements ci-dessous sont les elements du main menu
     * Car ils contiennent une propriété `icon`
     *
     ---------------------------------------------------  */
    {
      component: DiscoveryPage,
      disabled: false,
      icon: 'offres-w',
      // exemple d'URL optimale qui peut être partagée
      // par les sous composants
      path:
        '/decouverte/:offerId?/:mediationId?/:view(booking|verso)?/:bookingId?/:view(cancelled)?',
      title: 'Les offres',
    },
    {
      component: SearchContainer,
      disabled: false,
      icon: 'search-w',
      path:
        '/recherche/(resultats)?/:option?/:subOption?/:offerId?/:mediationIdOrView?/:view(booking)?/:bookingId?',
      title: 'Recherche',
    },
    {
      component: MyBookingsPage,
      disabled: false,
      icon: 'calendar-w',
      path: '/reservations',
      title: 'Mes réservations',
    },
    {
      component: FavoritesPage,
      disabled: true,
      icon: 'like-w',
      path: '/favoris',
      title: 'Mes préférés',
    },
    {
      component: ProfilePage,
      disabled: false,
      icon: 'user-w',
      path: '/profil/:view?/:status?',
      title: 'Mon compte',
    },
    {
      disabled: false,
      href: WEBAPP_CONTACT_EXTERNAL_PAGE,
      icon: 'help-w',
      target: '_blank',
      title: 'Aide',
    },
    {
      disabled: false,
      href:
        'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture',
      icon: 'txt-w',
      target: '_blank',
      title: 'Mentions légales',
    },
  ]
  return pipe(
    addMenuViewToRoutesWithPath,
    removeDisabledRoutes,
    extendRoutesWithExact,
  )(featuredRoutes)
}
