/**
 * Configure TomSelect on a `<select />`.
 *
 * We have two types of tom select instances:
 * 1. select field with static options,
 * 2. select field with dynamic options (xhr autocomplete).
 *
 * > Use `multiple` HTML attribut on `<select />` if needed.
 *
 * @example
 * // select field
 * <select class="pc-tom-select-field">
 *   <option value="1">item #1</option>
 *   <option value="2">item #2</option>
 * </select>
 *
 * @example
 * // select field with xhr autocomplete.
 * // In this example, our backend automatically sets data attributes, this allows the initial render to have the initialValues
 * <select
 *   class="pc-tom-select-field pc-tom-select-autocomplete-field"
 *   data-tomselect-autocomplete-url="/backofficev3/autocomplete/offerers"
 *   data-tomselect-options="[{\"id\": \"84\", \"text\": \"Cin\u00e9ma - CGR (00000003800058)\"}]"
 *   data-tomselect-items="[\"84\"]"
 * ></select>
 */
class PcTomSelectField extends PcAddOn {
  /** Unique identifier of this addon, in order to reference it from another add on */
  static ID = 'PcTomSelectFieldId'
  static PC_TOM_SELECT_FIELD_CLASS = 'pc-tom-select-field'
  static EMPTY_PC_TOM_SELECT_FIELD_CONTAINER_CLASS = 'empty-tom-select-form-container'
  static SELECT_SELECTOR = `select.${PcTomSelectField.PC_TOM_SELECT_FIELD_CLASS}`
  static SELECT_AUTOCOMPLETE_CLASS = 'pc-tom-select-autocomplete-field'
  static SELECT_SETTINGS = {
    plugins: ['dropdown_input', 'clear_button', 'checkbox_options'],
    persist: false,
    create: false,
  }

  state = {
    selects: []
  }

  get $selects() {
    return document.querySelectorAll(PcTomSelectField.SELECT_SELECTOR)
  }

  bindEvents = () => {
    this.$selects.forEach(($select) => {
      const settingsXhrAutocomplete = $select.classList.contains(PcTomSelectField.SELECT_AUTOCOMPLETE_CLASS) ?
        this.#getSettingsXhrAutocomplete($select) :
        {}
      if (!$select.tomselect) {
        this.state.selects.push(new TomSelect($select, {
          ...PcTomSelectField.SELECT_SETTINGS,
          ...settingsXhrAutocomplete,
        }))
      }
    })
    EventHandler.on(document.body, 'mousemove', PcTomSelectField.SELECT_SELECTOR, this._preventDefault)
    EventHandler.on(document.body, 'mousedown', PcTomSelectField.SELECT_SELECTOR, this.#onMouseDown)
    EventHandler.on(document.body, 'change', PcTomSelectField.SELECT_SELECTOR, this.#onScrollOrChange)
    EventHandler.on(document.body, 'scroll', PcTomSelectField.SELECT_SELECTOR, this.#onScrollOrChange)
  }

  unbindEvents = () => {
    // NOTE: destroy method unbind event but also destroy the HTML initialized by TomSelect which cause a UX glitch.
    // Since we do not have control nor want to maintain tom select lib, until a better method exist to unbind/rebind
    // We tolerate it's deactivation
    // See https://github.com/orchidjs/tom-select/discussions/569 for resolution
    // this.state.selects.forEach((select) => select.destroy())

    EventHandler.off(document.body, 'mousemove', PcTomSelectField.SELECT_SELECTOR, this._preventDefault)
    EventHandler.off(document.body, 'mousedown', PcTomSelectField.SELECT_SELECTOR, this.#onMouseDown)
    EventHandler.off(document.body, 'change', PcTomSelectField.SELECT_SELECTOR, this.#onScrollOrChange)
    EventHandler.off(document.body, 'scroll', PcTomSelectField.SELECT_SELECTOR, this.#onScrollOrChange)
  }

  #onMouseDown(event) {
    event.preventDefault()
    const scrollTop = event.target.scrollTop
    event.target.selected = !event.target.selected
    setTimeout(() => {
      event.target.scrollTop = scrollTop
    })
    event.target.focus()
  }

  #onScrollOrChange(event) {
    var selected = [...event.target.options].filter((option) => option.selected)

    if (selected.length > 0) {
      event.target.parentElement.querySelector('label').classList.add('d-none')
      return
    }
    event.target.parentElement.querySelector('label').classList.remove('d-none')
  }

  #getSettingsXhrAutocomplete($select) {
    const {
      tomselectAutocompleteUrl,
      tomselectOptions,
      tomselectItems,
    } = $select.dataset
    return {
      valueField: 'id',
      labelField: 'text',
      load: (query, callback) => {
        const url = `${tomselectAutocompleteUrl}?q=${encodeURIComponent(query)}`;
        fetch(url)
          .then((response) => response.json())
          .then((json) => callback(json.items))
          .catch((error) => callback(undefined, error))
      },
      render: {
        no_results: (data, escape) => {
          return '<div class="no-results">Aucun résultat pour "' + escape(data.input) + '"</div>'
        },
      },
      ...(tomselectOptions ? { options: JSON.parse(tomselectOptions) } : {}),
      ...(tomselectItems ? { items: JSON.parse(tomselectItems) } : {}),
    }
  }
}
