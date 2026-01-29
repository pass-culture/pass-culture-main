/**
 * Renders a postal address autocomplete that fills values in hidden inputs.
 *
 * It can be used when declaring form fields in the backend using `fields.PcPostalAddressAutocomplete`.
 *
 * > There is no HTML markup example as it uses a wtforms fields: `postal_address_autocomplete.html`
 *
 * @example
 * // We declare a field mapping to tell what field the autocomplete must set.
 * // None of them are mandatory, however, you must choose one so your autocomplete can submit something to the backend.
 *
 * postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
 *   "Adresse",
 *   street="street", // the name of your address field within your form, for its autocomplete to work
 *   banId="banId" // the unique id in the National Address Database (Base d'Adresses Nationale)
 *   inseeCode="inseeCode" // the code of the city (or code INSEE) in the National Address Database (Base d'Adresses Nationale)
 *   city="city", // the name of your city field within your form, for its autocomplete to work
 *   postalCode="postalCode", // the name of your postalCode field within your form, for its autocomplete to work
 *   latitude="latitude", // the name of your latitude field within your form, for its autocomplete to work
 *   longitude="longitude", // the name of your longitude field within your form, for its autocomplete to work
 *   required=True, // if True, it will add the required attribute to autocomplete the input (default: false)
 *   hasReset=True, // if True, it will add a reset-to-initial-values button (default: false)
 *   hasManualEditing=True, // if True, it will propose manual edition (default: false)
 *   limit=10, // limit of autocomplete choices (default: 10)
 * )
 * // Below are the hidden fields, you can decide to add form validators to them.
 * street = fields.PCOptStringField("street", initially_hidden=True) // if selected in the autocomplete, it will be filled in the form
 * city = fields.PCOptStringField("Ville", initially_hidden=True) // if selected in the autocomplete, it will be filled in the form
 * postalCode = fields.PCOptPostalCodeField("Code postal", initially_hidden=True) // if selected in the autocomplete, it will be filled in the form
 * latitude = fields.PCOptStringField("Latitude", initially_hidden=True) // if selected in the autocomplete, it will be filled in the form
 * longitude = fields.PCOptStringField("Longitude", initially_hidden=True) // if selected in the autocomplete, it will be filled in the form
 *
 */
class PcPostalAddressAutocomplete extends PcAddOn {

  static POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR = 'input[data-toggle="postal-address-autocomplete"]'
  static POSTAL_ADDRESS_AUTOCOMPLETE_RESET_SELECTOR = 'button.postal-address-autocomplete-reset'
  static POSTAL_ADDRESS_AUTOCOMPLETE_MANUAL_MODE_SELECTOR = 'button.postal-address-autocomplete-manual'
  static API_ADDRESS_DATA_GOUV_URL = 'https://data.geopf.fr/geocodage'
  static API_ADDRESS_DATA_GOUV_MIN_LIMIT = 3
  static API_ADDRESS_DATA_GOUV_MAX_LIMIT = 200
  static SEARCH_DEBOUNCE_DELAY_MS = 350
  static MANUAL_EDITION_OFF_LABEL = 'Édition manuelle'
  static MANUAL_EDITION_ON_LABEL = `Revenir à l'autocomplétion`
  state = {}

  get $autoCompletes() {
    return document.querySelectorAll(PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR)
  }

  initialize = () => {
    this.$autoCompletes.forEach(($autoComplete) => {
      // TODO: when <form> will always have a unique name, use it instead of action as unique key
      const name = $autoComplete.form.action
      if (!this.state[name]) {
        this.#prepareHtml($autoComplete)
      }
      const $postalCode = this.#getPostalCode($autoComplete)
      const $city = this.#getCity($autoComplete)
      const $street = this.#getStreet($autoComplete)
      const $banId = this.#getBanId($autoComplete)
      const $inseeCode = this.#getInseeCode($autoComplete)
      const $latitude = this.#getLatitude($autoComplete)
      const $longitude = this.#getLongitude($autoComplete)
      const $isManualAddress = this.#getIsManualAddress($autoComplete)
      this.state[name] = {
        cursorIndex: -1,
        initialValues: {
          required: $autoComplete.required,
          ...($postalCode ? { postalCode: $postalCode.value } : {}),
          ...($city ? { city: $city.value } : {}),
          ...($street ? { street: $street.value } : {}),
          ...($banId ? { banId: $banId.value } : {}),
          ...($inseeCode ? { inseeCode: $inseeCode.value } : {}),
          ...($latitude ? { latitude: $latitude.value } : {}),
          ...($longitude ? { longitude: $longitude.value } : {}),
          ...($isManualAddress ? { isManualAddress: $isManualAddress.value } : {}),
        }
      }

    })
    this._searchDebounce = PcUtils.debounce(this.#search, PcPostalAddressAutocomplete.SEARCH_DEBOUNCE_DELAY_MS)
  }

  bindEvents = () => {
    EventHandler.on(
      document,
      'keyup',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR,
      this.#onAddressChange
    )
    EventHandler.on(
      document,
      'keypress',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR,
      this._preventSubmitOnEnter
    )
    EventHandler.on(
      document,
      'blur',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR,
      this.#onBlur
    )
    EventHandler.on(
      document,
      'click',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_RESET_SELECTOR,
      this.#onResetForm
    )
    EventHandler.on(
      document,
      'click',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_MANUAL_MODE_SELECTOR,
      this.#onToggleManualEditing
    )
  }

  unbindEvents = () => {
    EventHandler.off(
      document,
      'keyup',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR,
      this.#onAddressChange
    )
    EventHandler.off(
      document,
      'keypress',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR,
      this._preventSubmitOnEnter
    )
    EventHandler.off(
      document,
      'blur',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR,
      this.#onBlur
    )
    EventHandler.off(
      document,
      'click',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_RESET_SELECTOR,
      this.#onResetForm
    )
    EventHandler.off(
      document,
      'click',
      PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_MANUAL_MODE_SELECTOR,
      this.#onToggleManualEditing
    )
  }

  #getApiUrl(limit) {
    return `${PcPostalAddressAutocomplete.API_ADDRESS_DATA_GOUV_URL}/search/?limit=${limit}`
  }

  #getStreet($autoComplete) {
    const { streetInputName } = $autoComplete.dataset
    return $autoComplete.form[streetInputName]
  }

  #getCity($autoComplete) {
    const { cityInputName } = $autoComplete.dataset
    return $autoComplete.form[cityInputName]
  }

  #getBanId($autoComplete) {
    const { banIdInputName } = $autoComplete.dataset
    return $autoComplete.form[banIdInputName]
  }

  #getInseeCode($autoComplete) {
    const { inseeCodeInputName } = $autoComplete.dataset
    return $autoComplete.form[inseeCodeInputName]
  }

  #getPostalCode($autoComplete) {
    const { postalCodeInputName } = $autoComplete.dataset
    return $autoComplete.form[postalCodeInputName]
  }

  #getLatitude($autoComplete) {
    const { latitudeInputName } = $autoComplete.dataset
    return $autoComplete.form[latitudeInputName]
  }

  #getLongitude($autoComplete) {
    const { longitudeInputName } = $autoComplete.dataset
    return $autoComplete.form[longitudeInputName]
  }

  #getIsManualAddress($autoComplete) {
    const { isManualAddressInputName } = $autoComplete.dataset
    return $autoComplete.form[isManualAddressInputName]
  }

  #getAutocompleteContainer($autoComplete) {
    return $autoComplete.parentElement
  }

  #getReset($autoComplete) {
    return this.#getAutocompleteContainer($autoComplete)
      .querySelector(PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_RESET_SELECTOR)
  }

  #getAutocompleteFromAnchorChoice($anchor) {
    // this following semantic is created internally within #prepareHtml
    return $anchor
      .parentElement  // anchor parent parent is li
      .parentElement  // li parent is ul
      .parentElement  // ul parent is the autocomplete container
      .querySelector(PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR)
  }

  #getDropdown($autoComplete) {
    return this.#getAutocompleteContainer($autoComplete)
      .querySelector('ul.dropdown-postal-address-autocomplete')
  }

  #getFeedback($autoComplete) {
    return this.#getAutocompleteContainer($autoComplete)
      .querySelector('div.feedback-postal-address-autocomplete')
  }

  #prepareHtml = ($autoComplete) => {
    $autoComplete.parentElement.classList.add('position-relative')

    const feedback = document.createElement("div")
    feedback.classList.add('invalid-feedback', 'feedback-postal-address-autocomplete')
    this.#getAutocompleteContainer($autoComplete).append(feedback)

    const dropdown = document.createElement("ul")
    dropdown.classList.add('dropdown-menu', 'shadow', 'dropdown-postal-address-autocomplete')
    dropdown.style.top = '3.55em'
    this.#getAutocompleteContainer($autoComplete).append(dropdown)
  }

  #onAddressChange = (event) => {
    event.preventDefault()
    const code = event.keyCode || event.which
    if ([
      KeyboardKeyCode.UP,
      KeyboardKeyCode.DOWN,
      KeyboardKeyCode.ENTER,
      KeyboardKeyCode.PAGEUP,
      KeyboardKeyCode.PAGEDOWN
    ].includes(code)) {
      this.#onManualIndexControl(event)
      return
    }

    if ([
      KeyboardKeyCode.SHIFT,
      KeyboardKeyCode.CTRL,
      KeyboardKeyCode.END,
      KeyboardKeyCode.HOME,
      KeyboardKeyCode.LEFT,
      KeyboardKeyCode.RIGHT,
    ].includes(code)) {
      return
    }

    this._searchDebounce(event)
  }

  #onManualIndexControl = (event) => {
    const code = event.keyCode || event.which
    const name = event.target.form.action

    if ([
      KeyboardKeyCode.UP,
      KeyboardKeyCode.DOWN,
      KeyboardKeyCode.PAGEUP,
      KeyboardKeyCode.PAGEDOWN
    ].includes(code)) {
      const $lis = [...this.#getDropdown(event.target).children]
      $lis.forEach(($li) => $li.querySelector('a').classList.remove('active'))
      if (KeyboardKeyCode.PAGEUP === code) {
        this.state[name].cursorIndex = 0
      } else if (KeyboardKeyCode.PAGEDOWN === code) {
        this.state[name].cursorIndex = $lis.length - 1
      } else {
        this.state[name].cursorIndex =
          KeyboardKeyCode.UP === code ?
            --this.state[name].cursorIndex :
            ++this.state[name].cursorIndex
        this.state[name].cursorIndex =
          this.state[name].cursorIndex < -1 ?
            -1 :
            this.state[name].cursorIndex
        this.state[name].cursorIndex =
          this.state[name].cursorIndex >= $lis.length ?
            $lis.length - 1 :
            this.state[name].cursorIndex
      }

      if (this.state[name].cursorIndex !== -1) {
        this.#getDropdown(event.target)
          .children[this.state[name].cursorIndex] // ul children is li
          .children[0].classList.add('active') // li first children is the anchor
      }
    }

    if (KeyboardKeyCode.ENTER === code) {
      if (this.state[name].cursorIndex !== -1) {
        this.#getDropdown(event.target).querySelector('.dropdown-menu a.active').click()
        this.state[name].cursorIndex = -1
      }
    }
  }

  #search = async (event) => {
    const query = event.target.value
    const { limit, hasReset, hasManualEditing } = event.target.dataset
    event.target.classList.add('is-invalid')

    if (Boolean(hasReset)) {
      this.#getReset(event.target).disabled = false
    }
    try {
      if (
        query.trim().length <= PcPostalAddressAutocomplete.API_ADDRESS_DATA_GOUV_MIN_LIMIT ||
        query.trim().length >= PcPostalAddressAutocomplete.API_ADDRESS_DATA_GOUV_MAX_LIMIT
      ) {
        return
      }
      event.target.classList.remove('is-valid')
      const response = await fetch(`${this.#getApiUrl(limit)}&q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: new Headers({
          'accept': 'application/json'
        })
      })
      if (!response.ok) {
        throw new Error(`API d'adresse en panne, ${hasManualEditing ? `utilisez l'édition manuelle` : `réessayez plus tard`}.`)
      }
      const { features } = await response.json()
      this.#setFeatures(event.target, features)
    } catch (error) {
      this.#setFeatures(event.target, [])
      this.#getFeedback(event.target).innerHTML = error.message
      this.#getFeedback(event.target).classList.add('is-invalid')
    }
  }

  #setFeatures = ($autoComplete, features) => {
    const $dropdown = this.#getDropdown($autoComplete)
    $dropdown.innerHTML = '';
    features
      .filter(({ properties }) => ['housenumber', 'street'].includes(properties.type)) // Filter API results to exclude municipalities and localities results
      .forEach(({ geometry, properties }) => {
        const { label, city, postcode: postalCode, name: street, id: banId, citycode: inseeCode } = properties
        const [longitude, latitude] = geometry.coordinates
        const li = document.createElement('li')
        const a = document.createElement('a')
        a.classList.add('dropdown-item')
        a.setAttribute('role', 'button')
        a.dataset.street = street
        a.dataset.banId = banId
        a.dataset.inseeCode = inseeCode
        a.dataset.postalCode = postalCode
        a.dataset.name = name
        a.dataset.city = city
        a.dataset.latitude = latitude
        a.dataset.longitude = longitude
        a.dataset.isManualAddress = ""
        a.onclick = this._onSelectFeature
        a.append(label)
        li.append(a)
        $dropdown.append(li)
    })
    if (features.length) {
      $dropdown.classList.add('show')
    }
  }

  _onSelectFeature = (event) => {
    event.preventDefault()
    const { street, banId, inseeCode, postalCode, city, latitude, longitude } = event.target.dataset
    const $autoComplete = this.#getAutocompleteFromAnchorChoice(event.target)
    this.#getDropdown($autoComplete).classList.remove('show')

    $autoComplete.classList.remove('is-invalid')
    $autoComplete.classList.add('is-valid')
    $autoComplete.value = `${street}, ${postalCode} ${city}`

    const $street = this.#getStreet($autoComplete)
    if ($street) {
      $street.value = street
    }

    const $banId = this.#getBanId($autoComplete)
    if ($banId) {
      $banId.value = banId
    }

    const $inseeCode = this.#getInseeCode($autoComplete)
    if ($inseeCode) {
      $inseeCode.value = inseeCode
    }

    const $postalCode = this.#getPostalCode($autoComplete)
    if ($postalCode) {
      $postalCode.value = postalCode
    }

    const $city = this.#getCity($autoComplete)
    if ($city) {
      $city.value = city
    }

    const $latitude = this.#getLatitude($autoComplete)
    if ($latitude) {
      $latitude.value = latitude
    }

    const $longitude = this.#getLongitude($autoComplete)
    if ($longitude) {
      $longitude.value = longitude
    }

    const $isManualAddress = this.#getIsManualAddress($autoComplete)
    if ($isManualAddress) {
      $isManualAddress.value = ""
    }
  }

  #onBlur = (event) => {
    // this timeout is useful to skip blur when clicking a valid choice
    setTimeout(() => {
      const $dropdown = this.#getDropdown(event.target)
      if ($dropdown.classList.contains('show')) {
        this.#getDropdown(event.target).classList.remove('show')
        this.#resetForm(event.target)
      }
    }, 500)
  }

  #onResetForm = (event) => {
    const $autoComplete = event.target.parentElement.parentElement.querySelector(PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR)
    this.#resetForm($autoComplete)
  }

  #resetForm = ($autoComplete) => {
    const { hasReset } = $autoComplete.dataset
    if (!Boolean(hasReset)) {
      return
    }
    const name = $autoComplete.form.action
    const {
      required,
      postalCode,
      city,
      street,
      banId,
      inseeCode,
      latitude,
      longitude,
      isManualAddress,
    } = this.state[name].initialValues
    $autoComplete.value = `${street}, ${postalCode} ${city}`
    $autoComplete.classList.remove('is-invalid', 'is-valid')

    const $postalCode = this.#getPostalCode($autoComplete)
    const $city = this.#getCity($autoComplete)
    const $street = this.#getStreet($autoComplete)
    const $banId = this.#getBanId($autoComplete)
    const $inseeCode = this.#getInseeCode($autoComplete)
    const $latitude = this.#getLatitude($autoComplete)
    const $longitude = this.#getLongitude($autoComplete)
    const $isManualAddress = this.#getIsManualAddress($autoComplete)
    $autoComplete.required = required

    if ($postalCode) {
      $postalCode.value = postalCode
    }
    if ($city) {
      $city.value = city
    }
    if ($street) {
      $street.value = street
    }
    if ($banId) {
      $banId.value = banId
    }
    if ($inseeCode) {
      $inseeCode.value = inseeCode
    }
    if ($latitude) {
      $latitude.value = latitude
    }
    if ($longitude) {
      $longitude.value = longitude
    }
    if ($isManualAddress) {
      $isManualAddress.value = $isManualAddress
    }

    this.#getReset($autoComplete).disabled = true
  }

  #onToggleManualEditing = (event) => {
    const $autoComplete = event.target
      .parentElement
      .parentElement.querySelector(PcPostalAddressAutocomplete.POSTAL_ADDRESS_AUTOCOMPLETE_SELECTOR)
    const name = $autoComplete.form.action
    const { required } = this.state[name].initialValues

    const $autoCompleteContainer = this.#getAutocompleteContainer($autoComplete)
    const $postalCode = this.#getPostalCode($autoComplete)
    const $city = this.#getCity($autoComplete)
    const $street = this.#getStreet($autoComplete)
    const $banId = this.#getBanId($autoComplete)
    const $inseeCode = this.#getInseeCode($autoComplete)
    const $latitude = this.#getLatitude($autoComplete)
    const $longitude = this.#getLongitude($autoComplete)
    const $isManualAddress = this.#getIsManualAddress($autoComplete)
    const isManualEditing = event.target.innerHTML.includes(PcPostalAddressAutocomplete.MANUAL_EDITION_OFF_LABEL)

    event.target.innerHTML = isManualEditing ?
      PcPostalAddressAutocomplete.MANUAL_EDITION_ON_LABEL :
      PcPostalAddressAutocomplete.MANUAL_EDITION_OFF_LABEL
    $autoCompleteContainer.classList[isManualEditing ? 'add' : 'remove']('d-none')


    $autoComplete.required = required === false ? required : !isManualEditing
    $autoComplete.disabled = isManualEditing

    if ($postalCode) {
      $postalCode.parentElement.classList[isManualEditing ? 'remove' : 'add']('d-none')
    }
    if ($city) {
      $city.parentElement.classList[isManualEditing ? 'remove' : 'add']('d-none')
    }
    if ($street) {
      $street.parentElement.classList[isManualEditing ? 'remove' : 'add']('d-none')
    }
    if ($latitude) {
      $latitude.parentElement.classList[isManualEditing ? 'remove' : 'add']('d-none')
    }
    if ($longitude) {
      $longitude.parentElement.classList[isManualEditing ? 'remove' : 'add']('d-none')
    }
    if (isManualEditing) {
      $isManualAddress.value = "on"
    } else {
      this.#resetForm($autoComplete)
    }
  }
}
