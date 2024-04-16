/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import { ApiOffresCollectivesService } from './services/ApiOffresCollectivesService';
import { DPrCiEApiContremarqueService } from './services/DPrCiEApiContremarqueService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class AppClientV2 {
  public readonly apiOffresCollectives: ApiOffresCollectivesService;
  public readonly dPrCiEApiContremarque: DPrCiEApiContremarqueService;
  public readonly request: BaseHttpRequest;
  constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? '',
      VERSION: config?.VERSION ?? '2',
      WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
      CREDENTIALS: config?.CREDENTIALS ?? 'include',
      TOKEN: config?.TOKEN,
      USERNAME: config?.USERNAME,
      PASSWORD: config?.PASSWORD,
      HEADERS: config?.HEADERS,
      ENCODE_PATH: config?.ENCODE_PATH,
    });
    this.apiOffresCollectives = new ApiOffresCollectivesService(this.request);
    this.dPrCiEApiContremarque = new DPrCiEApiContremarqueService(this.request);
  }
}

