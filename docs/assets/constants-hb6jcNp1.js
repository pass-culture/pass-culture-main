import{r as ct}from"./index-QQMyt9Ur.js";import"./config-BqmKEuqZ.js";import{u as lt}from"./chunk-S5YDGZLY-CNwzCxw0.js";/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Oe=function(e){const t=[];let a=0;for(let n=0;n<e.length;n++){let r=e.charCodeAt(n);r<128?t[a++]=r:r<2048?(t[a++]=r>>6|192,t[a++]=r&63|128):(r&64512)===55296&&n+1<e.length&&(e.charCodeAt(n+1)&64512)===56320?(r=65536+((r&1023)<<10)+(e.charCodeAt(++n)&1023),t[a++]=r>>18|240,t[a++]=r>>12&63|128,t[a++]=r>>6&63|128,t[a++]=r&63|128):(t[a++]=r>>12|224,t[a++]=r>>6&63|128,t[a++]=r&63|128)}return t},ut=function(e){const t=[];let a=0,n=0;for(;a<e.length;){const r=e[a++];if(r<128)t[n++]=String.fromCharCode(r);else if(r>191&&r<224){const s=e[a++];t[n++]=String.fromCharCode((r&31)<<6|s&63)}else if(r>239&&r<365){const s=e[a++],i=e[a++],o=e[a++],c=((r&7)<<18|(s&63)<<12|(i&63)<<6|o&63)-65536;t[n++]=String.fromCharCode(55296+(c>>10)),t[n++]=String.fromCharCode(56320+(c&1023))}else{const s=e[a++],i=e[a++];t[n++]=String.fromCharCode((r&15)<<12|(s&63)<<6|i&63)}}return t.join("")},ht={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const a=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,n=[];for(let r=0;r<e.length;r+=3){const s=e[r],i=r+1<e.length,o=i?e[r+1]:0,c=r+2<e.length,l=c?e[r+2]:0,f=s>>2,h=(s&3)<<4|o>>4;let d=(o&15)<<2|l>>6,E=l&63;c||(E=64,i||(d=64)),n.push(a[f],a[h],a[d],a[E])}return n.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Oe(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):ut(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const a=t?this.charToByteMapWebSafe_:this.charToByteMap_,n=[];for(let r=0;r<e.length;){const s=a[e.charAt(r++)],o=r<e.length?a[e.charAt(r)]:0;++r;const l=r<e.length?a[e.charAt(r)]:64;++r;const h=r<e.length?a[e.charAt(r)]:64;if(++r,s==null||o==null||l==null||h==null)throw new dt;const d=s<<2|o>>4;if(n.push(d),l!==64){const E=o<<4&240|l>>2;if(n.push(E),h!==64){const A=l<<6&192|h;n.push(A)}}}return n},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class dt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const ft=function(e){const t=Oe(e);return ht.encodeByteArray(t,!0)},Le=function(e){return ft(e).replace(/\./g,"")};function gt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function Q(){try{return typeof indexedDB=="object"}catch{return!1}}function Re(){return new Promise((e,t)=>{try{let a=!0;const n="validate-browser-context-for-indexeddb-analytics-module",r=self.indexedDB.open(n);r.onsuccess=()=>{r.result.close(),a||self.indexedDB.deleteDatabase(n),e(!0)},r.onupgradeneeded=()=>{a=!1},r.onerror=()=>{t(r.error?.message||"")}}catch(a){t(a)}})}function pt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const mt="FirebaseError";class y extends Error{constructor(t,a,n){super(a),this.code=t,this.customData=n,this.name=mt,Object.setPrototypeOf(this,y.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,k.prototype.create)}}class k{constructor(t,a,n){this.service=t,this.serviceName=a,this.errors=n}create(t,...a){const n=a[0]||{},r=`${this.service}/${t}`,s=this.errors[t],i=s?Ct(s,n):"Error",o=`${this.serviceName}: ${i} (${r}).`;return new y(r,o,n)}}function Ct(e,t){return e.replace(_t,(a,n)=>{const r=t[n];return r!=null?String(r):`<${n}?>`})}const _t=/\{\$([^}]+)}/g;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Et=1e3,It=2,bt=4*60*60*1e3,St=.5;function q(e,t=Et,a=It){const n=t*Math.pow(a,e),r=Math.round(St*n*(Math.random()-.5)*2);return Math.min(bt,n+r)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Fe(e){return e&&e._delegate?e._delegate:e}class w{constructor(t,a,n){this.name=t,this.instanceFactory=a,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const wt={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Tt=u.INFO,yt={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},At=(e,t,...a)=>{if(t<e.logLevel)return;const n=new Date().toISOString(),r=yt[t];if(r)console[r](`[${n}]  ${e.name}:`,...a);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class Z{constructor(t){this.name=t,this._logLevel=Tt,this._logHandler=At,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?wt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Dt=(e,t)=>t.some(a=>e instanceof a);let ce,le;function Ot(){return ce||(ce=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Lt(){return le||(le=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Pe=new WeakMap,z=new WeakMap,Me=new WeakMap,v=new WeakMap,ee=new WeakMap;function Rt(e){const t=new Promise((a,n)=>{const r=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{a(S(e.result)),r()},i=()=>{n(e.error),r()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(a=>{a instanceof IDBCursor&&Pe.set(a,e)}).catch(()=>{}),ee.set(t,e),t}function Ft(e){if(z.has(e))return;const t=new Promise((a,n)=>{const r=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{a(),r()},i=()=>{n(e.error||new DOMException("AbortError","AbortError")),r()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});z.set(e,t)}let Y={get(e,t,a){if(e instanceof IDBTransaction){if(t==="done")return z.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Me.get(e);if(t==="store")return a.objectStoreNames[1]?void 0:a.objectStore(a.objectStoreNames[0])}return S(e[t])},set(e,t,a){return e[t]=a,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Pt(e){Y=e(Y)}function Mt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...a){const n=e.call(H(this),t,...a);return Me.set(n,t.sort?t.sort():[t]),S(n)}:Lt().includes(e)?function(...t){return e.apply(H(this),t),S(Pe.get(this))}:function(...t){return S(e.apply(H(this),t))}}function kt(e){return typeof e=="function"?Mt(e):(e instanceof IDBTransaction&&Ft(e),Dt(e,Ot())?new Proxy(e,Y):e)}function S(e){if(e instanceof IDBRequest)return Rt(e);if(v.has(e))return v.get(e);const t=kt(e);return t!==e&&(v.set(e,t),ee.set(t,e)),t}const H=e=>ee.get(e);function ke(e,t,{blocked:a,upgrade:n,blocking:r,terminated:s}={}){const i=indexedDB.open(e,t),o=S(i);return n&&i.addEventListener("upgradeneeded",c=>{n(S(i.result),c.oldVersion,c.newVersion,S(i.transaction),c)}),a&&i.addEventListener("blocked",c=>a(c.oldVersion,c.newVersion,c)),o.then(c=>{s&&c.addEventListener("close",()=>s()),r&&c.addEventListener("versionchange",l=>r(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const Nt=["get","getKey","getAll","getAllKeys","count"],Bt=["put","add","delete","clear"],V=new Map;function ue(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(V.get(t))return V.get(t);const a=t.replace(/FromIndex$/,""),n=t!==a,r=Bt.includes(a);if(!(a in(n?IDBIndex:IDBObjectStore).prototype)||!(r||Nt.includes(a)))return;const s=async function(i,...o){const c=this.transaction(i,r?"readwrite":"readonly");let l=c.store;return n&&(l=l.index(o.shift())),(await Promise.all([l[a](...o),r&&c.done]))[0]};return V.set(t,s),s}Pt(e=>({...e,get:(t,a,n)=>ue(t,a)||e.get(t,a,n),has:(t,a)=>!!ue(t,a)||e.has(t,a)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class $t{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(a=>{if(Kt(a)){const n=a.getImmediate();return`${n.library}/${n.version}`}else return null}).filter(a=>a).join(" ")}}function Kt(e){return e.getComponent()?.type==="VERSION"}const X="@firebase/app",he="0.14.2";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const _=new Z("@firebase/app"),vt="@firebase/app-compat",Ht="@firebase/analytics-compat",Vt="@firebase/analytics",Ut="@firebase/app-check-compat",xt="@firebase/app-check",jt="@firebase/auth",Gt="@firebase/auth-compat",Wt="@firebase/database",qt="@firebase/data-connect",zt="@firebase/database-compat",Yt="@firebase/functions",Xt="@firebase/functions-compat",Jt="@firebase/installations",Qt="@firebase/installations-compat",Zt="@firebase/messaging",ea="@firebase/messaging-compat",ta="@firebase/performance",aa="@firebase/performance-compat",na="@firebase/remote-config",ra="@firebase/remote-config-compat",sa="@firebase/storage",ia="@firebase/storage-compat",oa="@firebase/firestore",ca="@firebase/ai",la="@firebase/firestore-compat",ua="firebase",ha="12.2.0",da={[X]:"fire-core",[vt]:"fire-core-compat",[Vt]:"fire-analytics",[Ht]:"fire-analytics-compat",[xt]:"fire-app-check",[Ut]:"fire-app-check-compat",[jt]:"fire-auth",[Gt]:"fire-auth-compat",[Wt]:"fire-rtdb",[qt]:"fire-data-connect",[zt]:"fire-rtdb-compat",[Yt]:"fire-fn",[Xt]:"fire-fn-compat",[Jt]:"fire-iid",[Qt]:"fire-iid-compat",[Zt]:"fire-fcm",[ea]:"fire-fcm-compat",[ta]:"fire-perf",[aa]:"fire-perf-compat",[na]:"fire-rc",[ra]:"fire-rc-compat",[sa]:"fire-gcs",[ia]:"fire-gcs-compat",[oa]:"fire-fst",[la]:"fire-fst-compat",[ca]:"fire-vertex","fire-js":"fire-js",[ua]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const fa=new Map,ga=new Map,de=new Map;function fe(e,t){try{e.container.addComponent(t)}catch(a){_.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,a)}}function T(e){const t=e.name;if(de.has(t))return _.debug(`There were multiple attempts to register component ${t}.`),!1;de.set(t,e);for(const a of fa.values())fe(a,e);for(const a of ga.values())fe(a,e);return!0}function Ne(e,t){const a=e.container.getProvider("heartbeat").getImmediate({optional:!0});return a&&a.triggerHeartbeat(),e.container.getProvider(t)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const pa={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},te=new k("app","Firebase",pa);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ma=ha;function C(e,t,a){let n=da[e]??e;a&&(n+=`-${a}`);const r=n.match(/\s|\//),s=t.match(/\s|\//);if(r||s){const i=[`Unable to register library "${n}" with version "${t}":`];r&&i.push(`library name "${n}" contains illegal characters (whitespace or "/")`),r&&s&&i.push("and"),s&&i.push(`version name "${t}" contains illegal characters (whitespace or "/")`),_.warn(i.join(" "));return}T(new w(`${n}-version`,()=>({library:n,version:t}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ca="firebase-heartbeat-database",_a=1,M="firebase-heartbeat-store";let U=null;function Be(){return U||(U=ke(Ca,_a,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(M)}catch(a){console.warn(a)}}}}).catch(e=>{throw te.create("idb-open",{originalErrorMessage:e.message})})),U}async function Ea(e){try{const a=(await Be()).transaction(M),n=await a.objectStore(M).get($e(e));return await a.done,n}catch(t){if(t instanceof y)_.warn(t.message);else{const a=te.create("idb-get",{originalErrorMessage:t?.message});_.warn(a.message)}}}async function ge(e,t){try{const n=(await Be()).transaction(M,"readwrite");await n.objectStore(M).put(t,$e(e)),await n.done}catch(a){if(a instanceof y)_.warn(a.message);else{const n=te.create("idb-set",{originalErrorMessage:a?.message});_.warn(n.message)}}}function $e(e){return`${e.name}!${e.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ia=1024,ba=30;class Sa{constructor(t){this.container=t,this._heartbeatsCache=null;const a=this.container.getProvider("app").getImmediate();this._storage=new Ta(a),this._heartbeatsCachePromise=this._storage.read().then(n=>(this._heartbeatsCache=n,n))}async triggerHeartbeat(){try{const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),n=pe();if(this._heartbeatsCache?.heartbeats==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,this._heartbeatsCache?.heartbeats==null)||this._heartbeatsCache.lastSentHeartbeatDate===n||this._heartbeatsCache.heartbeats.some(r=>r.date===n))return;if(this._heartbeatsCache.heartbeats.push({date:n,agent:a}),this._heartbeatsCache.heartbeats.length>ba){const r=ya(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(r,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(t){_.warn(t)}}async getHeartbeatsHeader(){try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache?.heartbeats==null||this._heartbeatsCache.heartbeats.length===0)return"";const t=pe(),{heartbeatsToSend:a,unsentEntries:n}=wa(this._heartbeatsCache.heartbeats),r=Le(JSON.stringify({version:2,heartbeats:a}));return this._heartbeatsCache.lastSentHeartbeatDate=t,n.length>0?(this._heartbeatsCache.heartbeats=n,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),r}catch(t){return _.warn(t),""}}}function pe(){return new Date().toISOString().substring(0,10)}function wa(e,t=Ia){const a=[];let n=e.slice();for(const r of e){const s=a.find(i=>i.agent===r.agent);if(s){if(s.dates.push(r.date),me(a)>t){s.dates.pop();break}}else if(a.push({agent:r.agent,dates:[r.date]}),me(a)>t){a.pop();break}n=n.slice(1)}return{heartbeatsToSend:a,unsentEntries:n}}class Ta{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Q()?Re().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const a=await Ea(this.app);return a?.heartbeats?a:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){if(await this._canUseIndexedDBPromise){const n=await this.read();return ge(this.app,{lastSentHeartbeatDate:t.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){if(await this._canUseIndexedDBPromise){const n=await this.read();return ge(this.app,{lastSentHeartbeatDate:t.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:[...n.heartbeats,...t.heartbeats]})}else return}}function me(e){return Le(JSON.stringify({version:2,heartbeats:e})).length}function ya(e){if(e.length===0)return-1;let t=0,a=e[0].date;for(let n=1;n<e.length;n++)e[n].date<a&&(a=e[n].date,t=n);return t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Aa(e){T(new w("platform-logger",t=>new $t(t),"PRIVATE")),T(new w("heartbeat",t=>new Sa(t),"PRIVATE")),C(X,he,e),C(X,he,"esm2020"),C("fire-js","")}Aa("");const Ke="@firebase/installations",ae="0.6.19";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ve=1e4,He=`w:${ae}`,Ve="FIS_v2",Da="https://firebaseinstallations.googleapis.com/v1",Oa=60*60*1e3,La="installations",Ra="Installations";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Fa={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},L=new k(La,Ra,Fa);function Ue(e){return e instanceof y&&e.code.includes("request-failed")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function xe({projectId:e}){return`${Da}/projects/${e}/installations`}function je(e){return{token:e.token,requestStatus:2,expiresIn:Ma(e.expiresIn),creationTime:Date.now()}}async function Ge(e,t){const n=(await t.json()).error;return L.create("request-failed",{requestName:e,serverCode:n.code,serverMessage:n.message,serverStatus:n.status})}function We({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Pa(e,{refreshToken:t}){const a=We(e);return a.append("Authorization",ka(t)),a}async function qe(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Ma(e){return Number(e.replace("s","000"))}function ka(e){return`${Ve} ${e}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Na({appConfig:e,heartbeatServiceProvider:t},{fid:a}){const n=xe(e),r=We(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={fid:a,authVersion:Ve,appId:e.appId,sdkVersion:He},o={method:"POST",headers:r,body:JSON.stringify(i)},c=await qe(()=>fetch(n,o));if(c.ok){const l=await c.json();return{fid:l.fid||a,registrationStatus:2,refreshToken:l.refreshToken,authToken:je(l.authToken)}}else throw await Ge("Create Installation",c)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ze(e){return new Promise(t=>{setTimeout(t,e)})}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ba(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const $a=/^[cdef][\w-]{21}$/,J="";function Ka(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const a=va(e);return $a.test(a)?a:J}catch{return J}}function va(e){return Ba(e).substr(0,22)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $(e){return`${e.appName}!${e.appId}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ye=new Map;function Xe(e,t){const a=$(e);Je(a,t),Ha(a,t)}function Je(e,t){const a=Ye.get(e);if(a)for(const n of a)n(t)}function Ha(e,t){const a=Va();a&&a.postMessage({key:e,fid:t}),Ua()}let O=null;function Va(){return!O&&"BroadcastChannel"in self&&(O=new BroadcastChannel("[Firebase] FID Change"),O.onmessage=e=>{Je(e.data.key,e.data.fid)}),O}function Ua(){Ye.size===0&&O&&(O.close(),O=null)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const xa="firebase-installations-database",ja=1,R="firebase-installations-store";let x=null;function ne(){return x||(x=ke(xa,ja,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(R)}}})),x}async function B(e,t){const a=$(e),r=(await ne()).transaction(R,"readwrite"),s=r.objectStore(R),i=await s.get(a);return await s.put(t,a),await r.done,(!i||i.fid!==t.fid)&&Xe(e,t.fid),t}async function Qe(e){const t=$(e),n=(await ne()).transaction(R,"readwrite");await n.objectStore(R).delete(t),await n.done}async function K(e,t){const a=$(e),r=(await ne()).transaction(R,"readwrite"),s=r.objectStore(R),i=await s.get(a),o=t(i);return o===void 0?await s.delete(a):await s.put(o,a),await r.done,o&&(!i||i.fid!==o.fid)&&Xe(e,o.fid),o}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function re(e){let t;const a=await K(e.appConfig,n=>{const r=Ga(n),s=Wa(e,r);return t=s.registrationPromise,s.installationEntry});return a.fid===J?{installationEntry:await t}:{installationEntry:a,registrationPromise:t}}function Ga(e){const t=e||{fid:Ka(),registrationStatus:0};return Ze(t)}function Wa(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const r=Promise.reject(L.create("app-offline"));return{installationEntry:t,registrationPromise:r}}const a={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},n=qa(e,a);return{installationEntry:a,registrationPromise:n}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:za(e)}:{installationEntry:t}}async function qa(e,t){try{const a=await Na(e,t);return B(e.appConfig,a)}catch(a){throw Ue(a)&&a.customData.serverCode===409?await Qe(e.appConfig):await B(e.appConfig,{fid:t.fid,registrationStatus:0}),a}}async function za(e){let t=await Ce(e.appConfig);for(;t.registrationStatus===1;)await ze(100),t=await Ce(e.appConfig);if(t.registrationStatus===0){const{installationEntry:a,registrationPromise:n}=await re(e);return n||a}return t}function Ce(e){return K(e,t=>{if(!t)throw L.create("installation-not-found");return Ze(t)})}function Ze(e){return Ya(e)?{fid:e.fid,registrationStatus:0}:e}function Ya(e){return e.registrationStatus===1&&e.registrationTime+ve<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Xa({appConfig:e,heartbeatServiceProvider:t},a){const n=Ja(e,a),r=Pa(e,a),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={installation:{sdkVersion:He,appId:e.appId}},o={method:"POST",headers:r,body:JSON.stringify(i)},c=await qe(()=>fetch(n,o));if(c.ok){const l=await c.json();return je(l)}else throw await Ge("Generate Auth Token",c)}function Ja(e,{fid:t}){return`${xe(e)}/${t}/authTokens:generate`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function se(e,t=!1){let a;const n=await K(e.appConfig,s=>{if(!et(s))throw L.create("not-registered");const i=s.authToken;if(!t&&en(i))return s;if(i.requestStatus===1)return a=Qa(e,t),s;{if(!navigator.onLine)throw L.create("app-offline");const o=an(s);return a=Za(e,o),o}});return a?await a:n.authToken}async function Qa(e,t){let a=await _e(e.appConfig);for(;a.authToken.requestStatus===1;)await ze(100),a=await _e(e.appConfig);const n=a.authToken;return n.requestStatus===0?se(e,t):n}function _e(e){return K(e,t=>{if(!et(t))throw L.create("not-registered");const a=t.authToken;return nn(a)?{...t,authToken:{requestStatus:0}}:t})}async function Za(e,t){try{const a=await Xa(e,t),n={...t,authToken:a};return await B(e.appConfig,n),a}catch(a){if(Ue(a)&&(a.customData.serverCode===401||a.customData.serverCode===404))await Qe(e.appConfig);else{const n={...t,authToken:{requestStatus:0}};await B(e.appConfig,n)}throw a}}function et(e){return e!==void 0&&e.registrationStatus===2}function en(e){return e.requestStatus===2&&!tn(e)}function tn(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+Oa}function an(e){const t={requestStatus:1,requestTime:Date.now()};return{...e,authToken:t}}function nn(e){return e.requestStatus===1&&e.requestTime+ve<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function rn(e){const t=e,{installationEntry:a,registrationPromise:n}=await re(t);return n?n.catch(console.error):se(t).catch(console.error),a.fid}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function sn(e,t=!1){const a=e;return await on(a),(await se(a,t)).token}async function on(e){const{registrationPromise:t}=await re(e);t&&await t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function cn(e){if(!e||!e.options)throw j("App Configuration");if(!e.name)throw j("App Name");const t=["projectId","apiKey","appId"];for(const a of t)if(!e.options[a])throw j(a);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function j(e){return L.create("missing-app-config-values",{valueName:e})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const tt="installations",ln="installations-internal",un=e=>{const t=e.getProvider("app").getImmediate(),a=cn(t),n=Ne(t,"heartbeat");return{app:t,appConfig:a,heartbeatServiceProvider:n,_delete:()=>Promise.resolve()}},hn=e=>{const t=e.getProvider("app").getImmediate(),a=Ne(t,tt).getImmediate();return{getId:()=>rn(a),getToken:r=>sn(a,r)}};function dn(){T(new w(tt,un,"PUBLIC")),T(new w(ln,hn,"PRIVATE"))}dn();C(Ke,ae);C(Ke,ae,"esm2020");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ee="analytics",fn="firebase_id",gn="origin",pn=60*1e3,mn="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ie="https://www.googletagmanager.com/gtag/js";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const g=new Z("@firebase/analytics");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Cn={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},m=new k("analytics","Analytics",Cn);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function _n(e){if(!e.startsWith(ie)){const t=m.create("invalid-gtag-resource",{gtagURL:e});return g.warn(t.message),""}return e}function at(e){return Promise.all(e.map(t=>t.catch(a=>a)))}function En(e,t){let a;return window.trustedTypes&&(a=window.trustedTypes.createPolicy(e,t)),a}function In(e,t){const a=En("firebase-js-sdk-policy",{createScriptURL:_n}),n=document.createElement("script"),r=`${ie}?l=${e}&id=${t}`;n.src=a?a?.createScriptURL(r):r,n.async=!0,document.head.appendChild(n)}function bn(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Sn(e,t,a,n,r,s){const i=n[r];try{if(i)await t[i];else{const c=(await at(a)).find(l=>l.measurementId===r);c&&await t[c.appId]}}catch(o){g.error(o)}e("config",r,s)}async function wn(e,t,a,n,r){try{let s=[];if(r&&r.send_to){let i=r.send_to;Array.isArray(i)||(i=[i]);const o=await at(a);for(const c of i){const l=o.find(h=>h.measurementId===c),f=l&&t[l.appId];if(f)s.push(f);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",n,r||{})}catch(s){g.error(s)}}function Tn(e,t,a,n){async function r(s,...i){try{if(s==="event"){const[o,c]=i;await wn(e,t,a,o,c)}else if(s==="config"){const[o,c]=i;await Sn(e,t,a,n,o,c)}else if(s==="consent"){const[o,c]=i;e("consent",o,c)}else if(s==="get"){const[o,c,l]=i;e("get",o,c,l)}else if(s==="set"){const[o]=i;e("set",o)}else e(s,...i)}catch(o){g.error(o)}}return r}function yn(e,t,a,n,r){let s=function(...i){window[n].push(arguments)};return window[r]&&typeof window[r]=="function"&&(s=window[r]),window[r]=Tn(s,e,t,a),{gtagCore:s,wrappedGtag:window[r]}}function An(e){const t=window.document.getElementsByTagName("script");for(const a of Object.values(t))if(a.src&&a.src.includes(ie)&&a.src.includes(e))return a;return null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Dn=30,On=1e3;class Ln{constructor(t={},a=On){this.throttleMetadata=t,this.intervalMillis=a}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,a){this.throttleMetadata[t]=a}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const nt=new Ln;function Rn(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Fn(e){const{appId:t,apiKey:a}=e,n={method:"GET",headers:Rn(a)},r=mn.replace("{app-id}",t),s=await fetch(r,n);if(s.status!==200&&s.status!==304){let i="";try{const o=await s.json();o.error?.message&&(i=o.error.message)}catch{}throw m.create("config-fetch-failed",{httpStatus:s.status,responseMessage:i})}return s.json()}async function Pn(e,t=nt,a){const{appId:n,apiKey:r,measurementId:s}=e.options;if(!n)throw m.create("no-app-id");if(!r){if(s)return{measurementId:s,appId:n};throw m.create("no-api-key")}const i=t.getThrottleMetadata(n)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new Nn;return setTimeout(async()=>{o.abort()},pn),rt({appId:n,apiKey:r,measurementId:s},i,o,t)}async function rt(e,{throttleEndTimeMillis:t,backoffCount:a},n,r=nt){const{appId:s,measurementId:i}=e;try{await Mn(n,t)}catch(o){if(i)return g.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${o?.message}]`),{appId:s,measurementId:i};throw o}try{const o=await Fn(e);return r.deleteThrottleMetadata(s),o}catch(o){const c=o;if(!kn(c)){if(r.deleteThrottleMetadata(s),i)return g.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${c?.message}]`),{appId:s,measurementId:i};throw o}const l=Number(c?.customData?.httpStatus)===503?q(a,r.intervalMillis,Dn):q(a,r.intervalMillis),f={throttleEndTimeMillis:Date.now()+l,backoffCount:a+1};return r.setThrottleMetadata(s,f),g.debug(`Calling attemptFetch again in ${l} millis`),rt(e,f,n,r)}}function Mn(e,t){return new Promise((a,n)=>{const r=Math.max(t-Date.now(),0),s=setTimeout(a,r);e.addEventListener(()=>{clearTimeout(s),n(m.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function kn(e){if(!(e instanceof y)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Nn{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Bn(e,t,a,n,r){if(r&&r.global){e("event",a,n);return}else{const s=await t,i={...n,send_to:s};e("event",a,i)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function $n(){if(Q())try{await Re()}catch(e){return g.warn(m.create("indexeddb-unavailable",{errorInfo:e?.toString()}).message),!1}else return g.warn(m.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Kn(e,t,a,n,r,s,i){const o=Pn(e);o.then(d=>{a[d.measurementId]=d.appId,e.options.measurementId&&d.measurementId!==e.options.measurementId&&g.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${d.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(d=>g.error(d)),t.push(o);const c=$n().then(d=>{if(d)return n.getId()}),[l,f]=await Promise.all([o,c]);An(s)||In(s,l.measurementId),r("js",new Date);const h=i?.config??{};return h[gn]="firebase",h.update=!0,f!=null&&(h[fn]=f),r("config",l.measurementId,h),l.measurementId}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class vn{constructor(t){this.app=t}_delete(){return delete P[this.app.options.appId],Promise.resolve()}}let P={},Ie=[];const be={};let G="dataLayer",Hn="gtag",Se,st,we=!1;function Vn(){const e=[];if(gt()&&e.push("This is a browser extension environment."),pt()||e.push("Cookies are not available."),e.length>0){const t=e.map((n,r)=>`(${r+1}) ${n}`).join(" "),a=m.create("invalid-analytics-context",{errorInfo:t});g.warn(a.message)}}function Un(e,t,a){Vn();const n=e.options.appId;if(!n)throw m.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)g.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw m.create("no-api-key");if(P[n]!=null)throw m.create("already-exists",{id:n});if(!we){bn(G);const{wrappedGtag:s,gtagCore:i}=yn(P,Ie,be,G,Hn);st=s,Se=i,we=!0}return P[n]=Kn(e,Ie,be,t,Se,G,a),new vn(e)}function xn(e,t,a,n){e=Fe(e),Bn(st,P[e.app.options.appId],t,a,n).catch(r=>g.error(r))}const Te="@firebase/analytics",ye="0.10.18";function jn(){T(new w(Ee,(t,{options:a})=>{const n=t.getProvider("app").getImmediate(),r=t.getProvider("installations-internal").getImmediate();return Un(n,r,a)},"PUBLIC")),T(new w("analytics-internal",e,"PRIVATE")),C(Te,ye),C(Te,ye,"esm2020");function e(t){try{const a=t.getProvider(Ee).getImmediate();return{logEvent:(n,r,s)=>xn(a,n,r,s)}}catch(a){throw m.create("interop-component-reg-failed",{reason:a})}}}jn();const W="@firebase/remote-config",Ae="0.6.6";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Gn="remote-config",De=100;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Wn={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},p=new k("remoteconfig","Remote Config",Wn);function qn(e){const t=Fe(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class zn{constructor(t,a,n,r){this.client=t,this.storage=a,this.storageCache=n,this.logger=r}isCachedDataFresh(t,a){if(!a)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const n=Date.now()-a,r=n<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${n}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${r}.`),r}async fetch(t){const[a,n]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(n&&this.isCachedDataFresh(t.cacheMaxAgeMillis,a))return n;t.eTag=n&&n.eTag;const r=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return r.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(r)),await Promise.all(s),r}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Yn(e=navigator){return e.languages&&e.languages[0]||e.language}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Xn{constructor(t,a,n,r,s,i){this.firebaseInstallations=t,this.sdkVersion=a,this.namespace=n,this.projectId=r,this.apiKey=s,this.appId=i}async fetch(t){const[a,n]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:a,app_instance_id_token:n,app_id:this.appId,language_code:Yn(),custom_signals:t.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(s,c),f=new Promise((D,F)=>{t.signal.addEventListener(()=>{const oe=new Error("The operation was aborted.");oe.name="AbortError",F(oe)})});let h;try{await Promise.race([l,f]),h=await l}catch(D){let F="fetch-client-network";throw D?.name==="AbortError"&&(F="fetch-timeout"),p.create(F,{originalErrorMessage:D?.message})}let d=h.status;const E=h.headers.get("ETag")||void 0;let A,I;if(h.status===200){let D;try{D=await h.json()}catch(F){throw p.create("fetch-client-parse",{originalErrorMessage:F?.message})}A=D.entries,I=D.state}if(I==="INSTANCE_STATE_UNSPECIFIED"?d=500:I==="NO_CHANGE"?d=304:(I==="NO_TEMPLATE"||I==="EMPTY_CONFIG")&&(A={}),d!==304&&d!==200)throw p.create("fetch-status",{httpStatus:d});return{status:d,eTag:E,config:A}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Jn(e,t){return new Promise((a,n)=>{const r=Math.max(t-Date.now(),0),s=setTimeout(a,r);e.addEventListener(()=>{clearTimeout(s),n(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Qn(e){if(!(e instanceof y)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Zn{constructor(t,a){this.client=t,this.storage=a}async fetch(t){const a=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,a)}async attemptFetch(t,{throttleEndTimeMillis:a,backoffCount:n}){await Jn(t.signal,a);try{const r=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),r}catch(r){if(!Qn(r))throw r;const s={throttleEndTimeMillis:Date.now()+q(n),backoffCount:n+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const er=60*1e3,tr=12*60*60*1e3;class ar{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(t,a,n,r,s){this.app=t,this._client=a,this._storageCache=n,this._storage=r,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:er,minimumFetchIntervalMillis:tr},this.defaultConfig={}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function N(e,t){const a=e.target.error||void 0;return p.create(t,{originalErrorMessage:a&&a?.message})}const b="app_namespace_store",nr="firebase_remote_config",rr=1;function sr(){return new Promise((e,t)=>{try{const a=indexedDB.open(nr,rr);a.onerror=n=>{t(N(n,"storage-open"))},a.onsuccess=n=>{e(n.target.result)},a.onupgradeneeded=n=>{const r=n.target.result;switch(n.oldVersion){case 0:r.createObjectStore(b,{keyPath:"compositeKey"})}}}catch(a){t(p.create("storage-open",{originalErrorMessage:a?.message}))}})}class it{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}}class ir extends it{constructor(t,a,n,r=sr()){super(),this.appId=t,this.appName=a,this.namespace=n,this.openDbPromise=r}async setCustomSignals(t){const n=(await this.openDbPromise).transaction([b],"readwrite"),r=await this.getWithTransaction("custom_signals",n),s=ot(t,r||{});return await this.setWithTransaction("custom_signals",s,n),s}async getWithTransaction(t,a){return new Promise((n,r)=>{const s=a.objectStore(b),i=this.createCompositeKey(t);try{const o=s.get(i);o.onerror=c=>{r(N(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;n(l?l.value:void 0)}}catch(o){r(p.create("storage-get",{originalErrorMessage:o?.message}))}})}async setWithTransaction(t,a,n){return new Promise((r,s)=>{const i=n.objectStore(b),o=this.createCompositeKey(t);try{const c=i.put({compositeKey:o,value:a});c.onerror=l=>{s(N(l,"storage-set"))},c.onsuccess=()=>{r()}}catch(c){s(p.create("storage-set",{originalErrorMessage:c?.message}))}})}async get(t){const n=(await this.openDbPromise).transaction([b],"readonly");return this.getWithTransaction(t,n)}async set(t,a){const r=(await this.openDbPromise).transaction([b],"readwrite");return this.setWithTransaction(t,a,r)}async delete(t){const a=await this.openDbPromise;return new Promise((n,r)=>{const i=a.transaction([b],"readwrite").objectStore(b),o=this.createCompositeKey(t);try{const c=i.delete(o);c.onerror=l=>{r(N(l,"storage-delete"))},c.onsuccess=()=>{n()}}catch(c){r(p.create("storage-delete",{originalErrorMessage:c?.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}class or extends it{constructor(){super(...arguments),this.storage={}}async get(t){return Promise.resolve(this.storage[t])}async set(t,a){return this.storage[t]=a,Promise.resolve(void 0)}async delete(t){return this.storage[t]=void 0,Promise.resolve()}async setCustomSignals(t){const a=this.storage.custom_signals||{};return this.storage.custom_signals=ot(t,a),Promise.resolve(this.storage.custom_signals)}}function ot(e,t){const a={...t,...e},n=Object.fromEntries(Object.entries(a).filter(([r,s])=>s!==null).map(([r,s])=>typeof s=="number"?[r,s.toString()]:[r,s]));if(Object.keys(n).length>De)throw p.create("custom-signal-max-allowed-signals",{maxSignals:De});return n}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class cr{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),a=this.storage.getLastSuccessfulFetchTimestampMillis(),n=this.storage.getActiveConfig(),r=this.storage.getCustomSignals(),s=await t;s&&(this.lastFetchStatus=s);const i=await a;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await n;o&&(this.activeConfig=o);const c=await r;c&&(this.customSignals=c)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}async setCustomSignals(t){this.customSignals=await this.storage.setCustomSignals(t)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function lr(){T(new w(Gn,e,"PUBLIC").setMultipleInstances(!0)),C(W,Ae),C(W,Ae,"esm2020");function e(t,{options:a}){const n=t.getProvider("app").getImmediate(),r=t.getProvider("installations-internal").getImmediate(),{projectId:s,apiKey:i,appId:o}=n.options;if(!s)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!o)throw p.create("registration-app-id");const c=a?.templateId||"firebase",l=Q()?new ir(o,n.name,c):new or,f=new cr(l),h=new Z(W);h.logLevel=u.ERROR;const d=new Xn(r,ma,c,s,i,o),E=new Zn(d,l),A=new zn(E,l,f,h),I=new ar(n,A,f,l,h);return qn(I),I}}lr();const ur=e=>Object.fromEntries(new URLSearchParams(e)),hr=()=>{const e=lt(),t=ur(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},mr=()=>{const e=hr();return{logEvent:ct.useCallback((a,n)=>{},[e])}};var dr=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER="hasClickedConfirmedAddHeadlineOffer",e.CLICKED_DISCOVERED_HEADLINE_OFFER="hasClickedDiscoveredHeadlineOffer",e.CLICKED_VIEW_APP_HEADLINE_OFFER="hasClickedViewAppHeadlineOffer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_DUPLICATE_BOOKABLE_OFFER="hasClickedDuplicateBookableOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",e.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",e.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE="hasClickedSeeTemplateOfferExample",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.DRAG_OR_SELECTED_IMAGE="hasDragOrSelectedImage",e.CLICKED_SAVE_IMAGE="hasClickedSaveImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e.EXTRA_PRO_DATA="extra_pro_data",e.CLICKED_NEW_EVOLUTIONS="hasClickedNewEvolutions",e.CLICKED_CONSULT_HELP="hasClickedConsultHelp",e.UPDATED_BOOKING_LIMIT_DATE="hasUpdatedBookingLimitDate",e.CLICKED_GENERATE_TEMPLATE_DESCRIPTION="hasClickedGenerateTemplateDescription",e.UPDATED_EVENT_STOCK_FILTERS="hasUpdatedEventStockFilters",e.CLICKED_VALIDATE_ADD_RECURRENCE_DATES="hasClickedValidateAddRecurrenceDates",e.FAKE_DOOR_VIDEO_INTERESTED="fakeDoorVideoInterested",e.CLICKED_SORT_STOCKS_TABLE="hasClickedSortStocksTable",e.OFFER_FORM_VIDEO_URL_ERROR="videoUrlError",e))(dr||{});export{dr as E,mr as u};
