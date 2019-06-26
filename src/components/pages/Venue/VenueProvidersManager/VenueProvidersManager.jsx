import classnames from 'classnames'
import React, { Component } from 'react'
import { requestData } from 'redux-saga-data'
import { Field, Form } from 'react-final-form'
import { showNotification } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import ReactTooltip from 'react-tooltip'
import Icon from '../../../layout/Icon'
import { HiddenField, TextField } from '../../../layout/form/fields'
import VenueProviderItem from './VenueProviderItem/VenueProviderItem'

const DEFAULT_OPTION = {
  id: 'default',
  name: 'Choix de la source'
}

export const FormRendered = ({
                               providers,
                               isProviderSelected,
                               isLoadingMode,
                               isCreationMode,
                               selectedValue,
                               handleChange
                             }) => {
  return ({handleSubmit}) => (
    <form onSubmit={handleSubmit}>
      <div className="provider-table">
        <HiddenField name="id"/>

        {providers && providers.length > 1 && (
          <React.Fragment>
            <div className="provider-picto">
              <span className="field picto">
                <Icon svg="picto-db-default"/>
              </span>
            </div>

            <Field
              name="providerId"
              required
              render={({input}) => {
                return (
                  <select
                    {...input}
                    className="field-select select-provider"
                    onChange={handleChange}
                    value={selectedValue.id}
                  >
                    <option value={DEFAULT_OPTION.id} key={DEFAULT_OPTION.id}>{DEFAULT_OPTION.name}</option>
                    {providers.map((provider) => (
                      <option value={provider.id} key={provider.id}>{provider.name}</option>
                    ))}
                  </select>
                )
              }}
            >
            </Field>

          </React.Fragment>
        )}

        {isProviderSelected && (
          <div className="venue-id-at-offer-provider-container">
            <TextField
              className={classnames('field-text fs12', {
                'field-is-read-only': isLoadingMode,
              })}
              label="Compte : "
              name="venueIdAtOfferProvider"
              readOnly={isLoadingMode}
              required
            />

            {isLoadingMode && (
              <div className="import-label-container">
                <span className="fs12 has-text-weight-semibold">
                    Importation en cours. Cette étape peut durer plusieurs dizaines de minutes.
                </span>
              </div>
            )}
          </div>
        )}

        {isProviderSelected && !isLoadingMode && (
          <span
            className="tooltip tooltip-info"
            data-place="bottom"
            data-tip={`<p>Veuillez saisir un identifiant.</p>`}
          >
              <Icon svg="picto-info"/>
            </span>
        )}

        {isProviderSelected && isCreationMode && !isLoadingMode && (
          <div className="button-provider-import-container">
            <button
              className="button is-intermediate button-provider-import"
              type="submit"
            >
              Importer
            </button>
          </div>
        )}
      </div>
    </form>
  )
}

class VenueProvidersManager extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isCreationMode: false,
      isLoadingMode: false,
      isProviderSelected: false,
      selectedValue: DEFAULT_OPTION.id
    }
  }

  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: {
        params: {venueProviderId},
      },
    } = nextProps
    const isCreationMode = venueProviderId === 'nouveau'

    return {
      isCreationMode,
    }
  }

  addVenueProvider = () => {
    const {
      history,
      match: {
        params: {offererId, venueId},
      },
    } = this.props
    this.setState({
      isCreationMode: true
    })
    history.push(`/structures/${offererId}/lieux/${venueId}/fournisseurs/nouveau`)
  }

  loadProvidersAndVenueProviders = () => {
    const {
      dispatch,
      match: {
        params: {venueId},
      },
    } = this.props

    dispatch(
      requestData({
        apiPath: '/providers'
      })
    )
    dispatch(
      requestData({
        apiPath: `/venueProviders?venueId=${venueId}`,
      })
    )
  }

  resetFormState = () => {
    this.setState({
      isCreationMode: false,
      isLoadingMode: false,
      isProviderSelected: false,
      selectedValue: DEFAULT_OPTION
    })
  }

  handleSubmit = (formValues) => {
    const {dispatch} = this.props
    this.setState({isLoadingMode: true})
    const {id, venueIdAtOfferProvider} = formValues
    const providerId = this.state.selectedValue.id

    const payload = {
      providerId: providerId,
      venueIdAtOfferProvider,
      venueId: id
    }

    // TODO
    // 1. Afficher la bonne image en fonction du provider
    // 2. Déclencher le POST sur /venueProviders avec le bon payload
    // 3. Afficher l'icone de DB
    // 4. Côté API : déclencher la création des n offres associés aux n stocks
    // 5. Refaire un appel pour récupérer le nombre d'offres créés (afin de les afficher sur le front) -> this.loadProvidersAndVenueProviders()

    dispatch(requestData({
        apiPath: `/venueProviders`,
        body: payload,
        handleFail: this.handleFail,
        handleSuccess: this.handleSuccess,
        method: 'POST',
      })
    )
  }

  handleSuccess = () => {
    const {
      history,
      match: {
        params: {offererId, venueId},
      },
    } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  handleFail = () => {
    const {dispatch} = this.props

    dispatch(showNotification({
      text: 'Une erreur est survenue lors de l\'import.',
      type: 'fail',
    }))
    this.resetFormState()
  }

  handleChange = (event) => {
    const valueFromSelectInput = event.target.value

    if (valueFromSelectInput && valueFromSelectInput !== DEFAULT_OPTION.id) {
      this.setState({
        isProviderSelected: true,
        selectedValue: {
          id: valueFromSelectInput
        },
      })
    } else {
      this.resetFormState()
    }
  }

  componentDidMount() {
    this.loadProvidersAndVenueProviders()
  }

  render() {
    const {
      providers,
      venue,
      venueProviders,
    } = this.props
    const {isCreationMode, isLoadingMode, isProviderSelected, selectedValue} = this.state

    return (
      <div className="venue-providers-manager section">
        <h2 className="main-list-title">
          IMPORTATIONS D'OFFRES
          <span className="is-pulled-right is-size-7 has-text-grey">
            Si vous avez plusieurs comptes auprès de la même source, ajoutez-les
            successivement.
          </span>
        </h2>

        <ul
          className="main-list">
          {venueProviders.map((venueProvider) => (
            <VenueProviderItem
              key={venueProvider.id}
              venueProvider={venueProvider}
            />
          ))}

          {isCreationMode && (
            <li>
              <Form
                onSubmit={this.handleSubmit}
                initialValues={venue}
                render={FormRendered({
                  providers,
                  isProviderSelected,
                  isLoadingMode,
                  isCreationMode,
                  selectedValue,
                  handleChange: this.handleChange
                })}
              />
            </li>
          )}
        </ul>
        <div className="has-text-centered">
          <button
            className="button is-secondary"
            disabled={isCreationMode}
            id="add-offer-btn"
            onClick={this.addVenueProvider}
            type="button"
          >
            + Importer des offres
          </button>
        </div>
      </div>
    )
  }
}

VenueProvidersManager.propTypes = {
  dispatch: PropTypes.func,
  history: PropTypes.shape(),
  match: PropTypes.shape({
    params: PropTypes.shape()
  }),
  providers: PropTypes.array,
  venue: PropTypes.shape(),
  venueProviders: PropTypes.array
}

export default VenueProvidersManager
