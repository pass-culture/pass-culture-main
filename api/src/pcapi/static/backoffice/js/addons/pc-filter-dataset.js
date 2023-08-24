/**
 * Search input that help filter element based on their dataset and then hide or show their container
 *
 * On search input:
 *
 * - `data-filter-dataset`: to enable this add on (required)
 * - `data-filter-context`: selector if you want to target a specific context (default `document.body`)
 * - `data-fields`: dataset fields used for filtering
 * - `data-on`: selector on which to read dataset on (required)
 * - `data-normalise`: set to `true` if you want to ignore accent
 * - `data-ignore-case`: set to `true` if you want to ignore case
 * - `data-exact`: set to `true` if you want an exact match
 *
 * Each element targeted with `data-on` must have a parent that contains the required class `pc-filter-dataset`.
 * This element will hide/show depending on search result.
 *
 * @example
 * <div class="some-container">
 *   <form class="input-group my-3 px-1">
 *     <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
 *     <input type="text"
 *            class="form-control col-8 border-start-0"
 *            name="q"
 *            value=""
 *            data-filter-dataset
 *            data-fields="name,description"
 *            data-on="input[type='checkbox']"
 *            data-filter-context=".some-container"
 *            data-normalize="true"
 *            data-ignore-case="true"
 *            data-exact="false"
 *            aria-describedby="search-icon"
 *            placeholder="Ex : Gérer les offres, ..."/>
 *     <button class="btn btn-outline-dark" type="reset" title="supprimer le filtre"><i class="bi bi-x"></i></button>
 *   </form>
 *   <div class="pc-filter-dataset">
 *       <input type="checkbox" value="foo" name="example" data-description="foo" />
 *   </div>
 *  <div class="pc-filter-dataset">
 *       <input type="checkbox" value="bar" name="example" data-description="bar" />
 *   </div>
 * <div>
 */
class PcFilterDataset extends PcAddOn {
    static SEARCH_INPUT_SELECTOR = '[data-filter-dataset]'
    static SEARCH_DEBOUNCE_DELAY_MS = 350
    static PARENT_FILTER_DATASET_CLASS = 'pc-filter-dataset'
    static MAX_PARENT_LOOKUP = 10
    static DEFAULT_LOOKUP_DATA_FIELDS = ['description']

    initialize = () => {
        this._searchDebounce = PcUtils.debounce(this.#search, PcFilterDataset.SEARCH_DEBOUNCE_DELAY_MS)
    }

    bindEvents = () => {
        EventHandler.on(document.body, 'keyup', PcFilterDataset.SEARCH_INPUT_SELECTOR, this._searchDebounce)
        EventHandler.on(document.body, 'change', PcFilterDataset.SEARCH_INPUT_SELECTOR, this._searchDebounce)
        EventHandler.on(document.body, 'keypress', PcFilterDataset.SEARCH_INPUT_SELECTOR, this._preventSubmitOnEnter)
    }

    unbindEvents = () => {
        EventHandler.off(document.body, 'keyup', PcFilterDataset.SEARCH_INPUT_SELECTOR, this._searchDebounce)
        EventHandler.off(document.body, 'change', PcFilterDataset.SEARCH_INPUT_SELECTOR, this._searchDebounce)
        EventHandler.off(document.body, 'keypress', PcFilterDataset.SEARCH_INPUT_SELECTOR, this._preventSubmitOnEnter)
    }

    #search = (event) => {
        const { value, dataset } = event.target
        const { filterContext, fields, ignoreCase, normalize, on, exact } = dataset
        const lookupFields = fields ? fields.split(',') : PcFilterDataset.DEFAULT_LOOKUP_DATA_FIELDS
        const context = document.querySelector(filterContext) || document.body

        context.querySelectorAll(on)
            .forEach(($element) => {
                let parent = $element

                let limit = PcFilterDataset.MAX_PARENT_LOOKUP
                while (!parent.classList.contains(PcFilterDataset.PARENT_FILTER_DATASET_CLASS) && limit > 0) {
                    parent = parent.parentElement
                    limit -= 1
                }

                const hasMatch = lookupFields.map((f) => {
                    const a = this.#cleanText($element.dataset[f], { ignoreCase, normalize })
                    const b = this.#cleanText(value, { ignoreCase, normalize })
                    if (!exact) {
                        return a.includes(b)
                    }
                    return a === b
                })

                if (hasMatch.includes(true)) {
                    parent.classList.remove('d-none')
                } else {
                    parent.classList.add('d-none')
                }
            })
    }

    #cleanText(text, { ignoreCase, normalize }) {
        let txt = text
        if (ignoreCase) {
            txt = txt.toLowerCase()
        }
        if (normalize) {
            txt = txt
                .normalize('NFD')
                .replace(/\p{Diacritic}/gu, '')
        }
        return txt

    }
}
