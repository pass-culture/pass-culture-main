/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

import type {
  ChangePasswordBodyModel,
  ChangeProEmailBody,
  CheckTokenBodyModel,
  CookieConsentRequest,
  LoginUserBodyModel,
  NewPasswordBodyModel,
  ProAnonymizationEligibilityResponseModel,
  ProUserCreationBodyV2Model,
  ResetPasswordBodyModel,
  SharedCurrentUserResponseModel,
  SharedLoginUserResponseModel,
  SubmitReviewRequestModel,
  UserEmailValidationResponseModel,
  UserIdentityBodyModel,
  UserIdentityResponseModel,
  UserPhoneBodyModel,
  UserPhoneResponseModel,
  UserResetEmailBodyModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class Users<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name Anonymize
   * @summary anonymize <POST>
   * @request POST:/users/anonymize
   */
  anonymize = (params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/anonymize`,
      method: 'POST',
      ...params,
    })
  /**
   * No description
   *
   * @name GetProAnonymizationEligibility
   * @summary get_pro_anonymization_eligibility <GET>
   * @request GET:/users/anonymize/eligibility
   */
  getProAnonymizationEligibility = (params: RequestParams = {}) =>
    this.request<
      ProAnonymizationEligibilityResponseModel,
      void | ValidationError
    >({
      path: `/users/anonymize/eligibility`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PostCheckToken
   * @summary post_check_token <POST>
   * @request POST:/users/check-token
   */
  postCheckToken = (data: CheckTokenBodyModel, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/check-token`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name ConnectAs
   * @summary connect_as <GET>
   * @request GET:/users/connect-as/{token}
   */
  connectAs = (token: string, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/connect-as/${token}`,
      method: 'GET',
      ...params,
    })
  /**
   * No description
   *
   * @name CookiesConsent
   * @summary cookies_consent <POST>
   * @request POST:/users/cookies
   */
  cookiesConsent = (data: CookieConsentRequest, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/cookies`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetProfile
   * @summary get_profile <GET>
   * @request GET:/users/current
   */
  getProfile = (params: RequestParams = {}) =>
    this.request<SharedCurrentUserResponseModel, void | ValidationError>({
      path: `/users/current`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PostUserEmail
   * @summary post_user_email <POST>
   * @request POST:/users/email
   */
  postUserEmail = (data: UserResetEmailBodyModel, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/email`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetUserEmailPendingValidation
   * @summary get_user_email_pending_validation <GET>
   * @request GET:/users/email_pending_validation
   */
  getUserEmailPendingValidation = (params: RequestParams = {}) =>
    this.request<UserEmailValidationResponseModel, void | ValidationError>({
      path: `/users/email_pending_validation`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchUserIdentity
   * @summary patch_user_identity <PATCH>
   * @request PATCH:/users/identity
   */
  patchUserIdentity = (
    data: UserIdentityBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<UserIdentityResponseModel, void | ValidationError>({
      path: `/users/identity`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name SubmitUserReview
   * @summary submit_user_review <POST>
   * @request POST:/users/log-user-review
   */
  submitUserReview = (
    data: SubmitReviewRequestModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/users/log-user-review`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PostNewPassword
   * @summary post_new_password <POST>
   * @request POST:/users/new-password
   */
  postNewPassword = (data: NewPasswordBodyModel, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/new-password`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PostChangePassword
   * @summary post_change_password <POST>
   * @request POST:/users/password
   */
  postChangePassword = (
    data: ChangePasswordBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/users/password`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PatchUserPhone
   * @summary patch_user_phone <PATCH>
   * @request PATCH:/users/phone
   */
  patchUserPhone = (data: UserPhoneBodyModel, params: RequestParams = {}) =>
    this.request<UserPhoneResponseModel, void | ValidationError>({
      path: `/users/phone`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name ResetPassword
   * @summary reset_password <POST>
   * @request POST:/users/reset-password
   */
  resetPassword = (data: ResetPasswordBodyModel, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/reset-password`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PatchProUserRgsSeen
   * @summary patch_pro_user_rgs_seen <PATCH>
   * @request PATCH:/users/rgs-seen
   */
  patchProUserRgsSeen = (params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/rgs-seen`,
      method: 'PATCH',
      ...params,
    })
  /**
   * No description
   *
   * @name Signin
   * @summary signin <POST>
   * @request POST:/users/signin
   */
  signin = (data: LoginUserBodyModel, params: RequestParams = {}) =>
    this.request<SharedLoginUserResponseModel, void | ValidationError>({
      path: `/users/signin`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name Signout
   * @summary signout <GET>
   * @request GET:/users/signout
   */
  signout = (params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/signout`,
      method: 'GET',
      ...params,
    })
  /**
   * No description
   *
   * @name SignupPro
   * @summary signup_pro <POST>
   * @request POST:/users/signup
   */
  signupPro = (data: ProUserCreationBodyV2Model, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/signup`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PatchUserTutoSeen
   * @summary patch_user_tuto_seen <PATCH>
   * @request PATCH:/users/tuto-seen
   */
  patchUserTutoSeen = (params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/tuto-seen`,
      method: 'PATCH',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchValidateEmail
   * @summary patch_validate_email <PATCH>
   * @request PATCH:/users/validate_email
   */
  patchValidateEmail = (data: ChangeProEmailBody, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/validate_email`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name ValidateUser
   * @summary validate_user <PATCH>
   * @request PATCH:/users/validate_signup/{token}
   */
  validateUser = (token: string, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/users/validate_signup/${token}`,
      method: 'PATCH',
      ...params,
    })
}
