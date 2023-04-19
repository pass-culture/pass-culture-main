/**
 * Add batch submit form to selection done using one `selectedRowsIds` within [PcTableMultiSelect](#pctablemultiselect).
 *
 * Form is renderer through a turbo frame which must be loaded with `loading="true"`.
 *
 * > Current integration does not yet support modal rendered with turbo `loading="lazy"`.
 *
 * To work, each `.btn-group` must set the following attributes:
 * - `[data-toggle="pc-batch-confirm-btn-group"]`: this value is fixed,
 * - `[data-toggle-id]`: this value must be a unique identifier,
 * - `[data-pc-table-multi-select-id]`: this value must be a valid pc table multi select identifier,
 * - `[data-input-ids-name]`: this value is used as the input name for storing `selectedIds`.
 *
 * Within the `.btn-group` container, you can add as many buttons as needed, and you must set some attributes too:
 * - `[data-use-confirmation-modal]`: `true` to open a modal to add a comment or `false` to submit directly, (required)
 * - `[data-modal-selector]`: this value must be the modal selector that contains the form, (optional)
 * - `[data-url]`: this value is required when you do not use confirmation modal (`[data-use-confirmation-modal]`) and should be the `POST` endpoint,
 * - `[data-mode]`: set this attributes to `fetch` if you want to use a form data (requires a POST controller),
 * - `[data-fetch-url]`: URL that renders the form, it uses `POST` with the `selectedRowsIds` from table multi select.
 *
 * @example
 * <div
 *   class="btn-group btn-group-sm"
 *   data-toggle="pc-batch-confirm-btn-group"
 *   data-toggle-id="table-container-user-offerer-validation-btn-group"
 *   data-pc-table-multi-select-id="table-container-user-offerer-validation"
 *   data-input-ids-name="object_ids"
 * >
 *   <button
 *     disabled
 *     type="button"
 *     class="btn btn-outline-primary"
 *     data-url="{{ url_for("backoffice_v3_web.validation.batch_validate_user_offerer") }}"
 *     data-user-confirmation-modal="false"
 *   >
 *     Valider
 *   </button>
 *   <button
 *     disabled
 *     type="button"
 *     class="btn btn-outline-primary"
 *     data-use-confirmation-modal="true"
 *     data-modal-selector="#batch-pending-modal"
 *   >
 *     Mettre en attente
 *   </button>
 *   <button
 *     disabled
 *     type="button"
 *     class="btn btn-outline-primary"
 *     data-use-confirmation-modal="true"
 *     data-modal-selector="#batch-reject-modal"
 *   >
 *     Rejeter
 *   </button>
 * </div>
 *
 *  {{ build_lazy_modal(url_for("backoffice_v3_web.validation.get_batch_user_offerer_pending_form"), "batch-pending-modal", "true") }}
 *  {{ build_lazy_modal(url_for("backoffice_v3_web.validation.get_batch_reject_user_offerer_form"), "batch-reject-modal", "true") }}
 */
class PcBatchActionForm extends PcAddOn {
  static BATCH_CONFIRM_BTN_GROUP_SELECTOR = '[data-toggle="pc-batch-confirm-btn-group"]'
  static BATCH_CONFIRM_BTN_SELECTOR = 'button[data-use-confirmation-modal]'

  state = {}

  get $batchConfirmBtnGroups() {
    return document.querySelectorAll(PcBatchActionForm.BATCH_CONFIRM_BTN_GROUP_SELECTOR)
  }

  getBatchConfirmButtons($batchConfirmBtnGroup) {
    return $batchConfirmBtnGroup.querySelectorAll(PcBatchActionForm.BATCH_CONFIRM_BTN_SELECTOR)
  }

  initialize = () => {
    this.$batchConfirmBtnGroups.forEach(($batchConfirmBtnGroup) => {
      const { toggleId, pcTableMultiSelectId, inputIdsName } = $batchConfirmBtnGroup.dataset
      this.state[toggleId] = {
        inputIdsName,
      }

      this.getBatchConfirmButtons($batchConfirmBtnGroup).forEach(($button) => {
        $button.dataset.pcTableMultiSelectId = pcTableMultiSelectId
        $button.dataset.toggleId = toggleId
      })
    })
  }

  bindEvents = () => {
    addEventListener('pcTableMultiSelect:change', this.#onBatchSelectionChange)
    this.$batchConfirmBtnGroups.forEach(($batchConfirmBtnGroup) => {
      EventHandler.on($batchConfirmBtnGroup, 'click', PcBatchActionForm.BATCH_CONFIRM_BTN_SELECTOR, this.#onBatchButtonClick)
    })
  }

  unbindEvents = () => {
    removeEventListener('pcTableMultiSelect:change', this.#onBatchSelectionChange)
    this.$batchConfirmBtnGroups.forEach(($batchConfirmBtnGroup) => {
      EventHandler.off($batchConfirmBtnGroup, 'click', PcBatchActionForm.BATCH_CONFIRM_BTN_SELECTOR, this.#onBatchButtonClick)
    })
  }

  #onBatchSelectionChange = ({ detail }) => {
    const { selectedRowsIds, tableMultiSelectId } = detail
    this.state[tableMultiSelectId] = { selectedRowsIds }
    this.$batchConfirmBtnGroups.forEach(($batchConfirmBtnGroup) => {
      const { pcTableMultiSelectId } = $batchConfirmBtnGroup.dataset
      if (tableMultiSelectId !== pcTableMultiSelectId) {
        return
      }

      this.getBatchConfirmButtons($batchConfirmBtnGroup).forEach(($button) => {
        $button.disabled = selectedRowsIds.size === 0
      })
    })
  }

  #onBatchButtonClick = async (event) => {
    const { useConfirmationModal, pcTableMultiSelectId, toggleId, url, mode, fetchUrl } = event.target.dataset
    const { inputIdsName } = this.state[toggleId]
    const tableMultiSelectState = this.app.addons.pcTableMultiSelect.state[pcTableMultiSelectId]
    const idsStr = [...tableMultiSelectState.selectedRowsIds].join(',')

    if (url && useConfirmationModal !== 'true') {
      const $form = document.createElement('form')
      $form.classList.add('d-none')
      $form.method = 'post'
      $form.action = url
      $form.innerHTML = this.app.csrfTokenInput
      const $input = document.createElement('input')
      $input.type = 'hidden'
      $input.value = idsStr
      $input.name = inputIdsName
      $form.appendChild($input)
      document.body.appendChild($form)
      $form.submit()
      return
    }
    const $modal = document.querySelector(event.target.dataset.modalSelector)
    const $form = $modal.querySelector('form') // no support for turbo loading="lazy" yet
    const $objectIds = $form.querySelector(`input[name="${inputIdsName}"]`)
    $objectIds.value = idsStr

    if (mode === 'fetch' && fetchUrl) {
      try {
        const $turboFrame = $modal.querySelector('turbo-frame')
        const formData = new FormData()
        formData.append(inputIdsName, idsStr)
        formData.append('csrf_token', app.csrfTokenValue)
        const response = await fetch(fetchUrl, {
          method: 'POST',
          body: formData,
        })
        if (!response.ok) {
          throw new Error(`Bad response code (${response.status}): ${response.statusText}`)
        }
        this.app.addons.pcSelectMultipleField.unbindEvents()
        $turboFrame.parentElement.innerHTML = await response.text()
        this.app.addons.pcSelectMultipleField.bindEvents()
      } catch (error) {
        throw new Error(error)
      }
    }
    bootstrap.Modal.getOrCreateInstance($modal).show()
  }
}
