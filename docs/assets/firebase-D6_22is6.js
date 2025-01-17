import{r as G}from"./index-ClcD9ViR.js";import"./config-BdqymTTq.js";import{b as ut}from"./index-C3LhMar3.js";/**
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
 */const Re=function(t){const e=[];let n=0;for(let s=0;s<t.length;s++){let r=t.charCodeAt(s);r<128?e[n++]=r:r<2048?(e[n++]=r>>6|192,e[n++]=r&63|128):(r&64512)===55296&&s+1<t.length&&(t.charCodeAt(s+1)&64512)===56320?(r=65536+((r&1023)<<10)+(t.charCodeAt(++s)&1023),e[n++]=r>>18|240,e[n++]=r>>12&63|128,e[n++]=r>>6&63|128,e[n++]=r&63|128):(e[n++]=r>>12|224,e[n++]=r>>6&63|128,e[n++]=r&63|128)}return e},ht=function(t){const e=[];let n=0,s=0;for(;n<t.length;){const r=t[n++];if(r<128)e[s++]=String.fromCharCode(r);else if(r>191&&r<224){const a=t[n++];e[s++]=String.fromCharCode((r&31)<<6|a&63)}else if(r>239&&r<365){const a=t[n++],i=t[n++],o=t[n++],c=((r&7)<<18|(a&63)<<12|(i&63)<<6|o&63)-65536;e[s++]=String.fromCharCode(55296+(c>>10)),e[s++]=String.fromCharCode(56320+(c&1023))}else{const a=t[n++],i=t[n++];e[s++]=String.fromCharCode((r&15)<<12|(a&63)<<6|i&63)}}return e.join("")},dt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,s=[];for(let r=0;r<t.length;r+=3){const a=t[r],i=r+1<t.length,o=i?t[r+1]:0,c=r+2<t.length,l=c?t[r+2]:0,d=a>>2,h=(a&3)<<4|o>>4;let f=(o&15)<<2|l>>6,g=l&63;c||(g=64,i||(f=64)),s.push(n[d],n[h],n[f],n[g])}return s.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(Re(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):ht(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const n=e?this.charToByteMapWebSafe_:this.charToByteMap_,s=[];for(let r=0;r<t.length;){const a=n[t.charAt(r++)],o=r<t.length?n[t.charAt(r)]:0;++r;const l=r<t.length?n[t.charAt(r)]:64;++r;const h=r<t.length?n[t.charAt(r)]:64;if(++r,a==null||o==null||l==null||h==null)throw new ft;const f=a<<2|o>>4;if(s.push(f),l!==64){const g=o<<4&240|l>>2;if(s.push(g),h!==64){const _=l<<6&192|h;s.push(_)}}}return s},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}};class ft extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const gt=function(t){const e=Re(t);return dt.encodeByteArray(e,!0)},Oe=function(t){return gt(t).replace(/\./g,"")};function pt(){try{return typeof indexedDB=="object"}catch{return!1}}function mt(){return new Promise((t,e)=>{try{let n=!0;const s="validate-browser-context-for-indexeddb-analytics-module",r=self.indexedDB.open(s);r.onsuccess=()=>{r.result.close(),n||self.indexedDB.deleteDatabase(s),t(!0)},r.onupgradeneeded=()=>{n=!1},r.onerror=()=>{var a;e(((a=r.error)===null||a===void 0?void 0:a.message)||"")}}catch(n){e(n)}})}/**
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
 */const bt="FirebaseError";let ee=class Pe extends Error{constructor(e,n,s){super(n),this.code=e,this.customData=s,this.name=bt,Object.setPrototypeOf(this,Pe.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,$e.prototype.create)}},$e=class{constructor(e,n,s){this.service=e,this.serviceName=n,this.errors=s}create(e,...n){const s=n[0]||{},r=`${this.service}/${e}`,a=this.errors[e],i=a?wt(a,s):"Error",o=`${this.serviceName}: ${i} (${r}).`;return new ee(r,o,s)}};function wt(t,e){return t.replace(yt,(n,s)=>{const r=e[s];return r!=null?String(r):`<${s}?>`})}const yt=/\{\$([^}]+)}/g;let z=class{constructor(e,n,s){this.name=e,this.instanceFactory=n,this.type=s,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}};/**
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
 */var u;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(u||(u={}));const It={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},_t=u.INFO,Et={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},St=(t,e,...n)=>{if(e<t.logLevel)return;const s=new Date().toISOString(),r=Et[e];if(r)console[r](`[${s}]  ${t.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class te{constructor(e){this.name=e,this._logLevel=_t,this._logHandler=St,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in u))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?It[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...e),this._logHandler(this,u.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...e),this._logHandler(this,u.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,u.INFO,...e),this._logHandler(this,u.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,u.WARN,...e),this._logHandler(this,u.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...e),this._logHandler(this,u.ERROR,...e)}}const Tt=(t,e)=>e.some(n=>t instanceof n);let ue,he;function vt(){return ue||(ue=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Ct(){return he||(he=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Fe=new WeakMap,Y=new WeakMap,Be=new WeakMap,x=new WeakMap,ne=new WeakMap;function At(t){const e=new Promise((n,s)=>{const r=()=>{t.removeEventListener("success",a),t.removeEventListener("error",i)},a=()=>{n(T(t.result)),r()},i=()=>{s(t.error),r()};t.addEventListener("success",a),t.addEventListener("error",i)});return e.then(n=>{n instanceof IDBCursor&&Fe.set(n,t)}).catch(()=>{}),ne.set(e,t),e}function Dt(t){if(Y.has(t))return;const e=new Promise((n,s)=>{const r=()=>{t.removeEventListener("complete",a),t.removeEventListener("error",i),t.removeEventListener("abort",i)},a=()=>{n(),r()},i=()=>{s(t.error||new DOMException("AbortError","AbortError")),r()};t.addEventListener("complete",a),t.addEventListener("error",i),t.addEventListener("abort",i)});Y.set(t,e)}let J={get(t,e,n){if(t instanceof IDBTransaction){if(e==="done")return Y.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Be.get(t);if(e==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return T(t[e])},set(t,e,n){return t[e]=n,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function Mt(t){J=t(J)}function Rt(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...n){const s=t.call(j(this),e,...n);return Be.set(s,e.sort?e.sort():[e]),T(s)}:Ct().includes(t)?function(...e){return t.apply(j(this),e),T(Fe.get(this))}:function(...e){return T(t.apply(j(this),e))}}function Ot(t){return typeof t=="function"?Rt(t):(t instanceof IDBTransaction&&Dt(t),Tt(t,vt())?new Proxy(t,J):t)}function T(t){if(t instanceof IDBRequest)return At(t);if(x.has(t))return x.get(t);const e=Ot(t);return e!==t&&(x.set(t,e),ne.set(e,t)),e}const j=t=>ne.get(t);function Le(t,e,{blocked:n,upgrade:s,blocking:r,terminated:a}={}){const i=indexedDB.open(t,e),o=T(i);return s&&i.addEventListener("upgradeneeded",c=>{s(T(i.result),c.oldVersion,c.newVersion,T(i.transaction),c)}),n&&i.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),o.then(c=>{a&&c.addEventListener("close",()=>a()),r&&c.addEventListener("versionchange",l=>r(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const Pt=["get","getKey","getAll","getAllKeys","count"],$t=["put","add","delete","clear"],H=new Map;function de(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(H.get(e))return H.get(e);const n=e.replace(/FromIndex$/,""),s=e!==n,r=$t.includes(n);if(!(n in(s?IDBIndex:IDBObjectStore).prototype)||!(r||Pt.includes(n)))return;const a=async function(i,...o){const c=this.transaction(i,r?"readwrite":"readonly");let l=c.store;return s&&(l=l.index(o.shift())),(await Promise.all([l[n](...o),r&&c.done]))[0]};return H.set(e,a),a}Mt(t=>({...t,get:(e,n,s)=>de(e,n)||t.get(e,n,s),has:(e,n)=>!!de(e,n)||t.has(e,n)}));/**
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
 */class Ft{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(Bt(n)){const s=n.getImmediate();return`${s.library}/${s.version}`}else return null}).filter(n=>n).join(" ")}}function Bt(t){const e=t.getComponent();return(e==null?void 0:e.type)==="VERSION"}const X="@firebase/app",fe="0.10.17";/**
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
 */const I=new te("@firebase/app"),Lt="@firebase/app-compat",Nt="@firebase/analytics-compat",kt="@firebase/analytics",xt="@firebase/app-check-compat",jt="@firebase/app-check",Ht="@firebase/auth",Vt="@firebase/auth-compat",Ut="@firebase/database",Wt="@firebase/data-connect",qt="@firebase/database-compat",Kt="@firebase/functions",Gt="@firebase/functions-compat",zt="@firebase/installations",Yt="@firebase/installations-compat",Jt="@firebase/messaging",Xt="@firebase/messaging-compat",Qt="@firebase/performance",Zt="@firebase/performance-compat",en="@firebase/remote-config",tn="@firebase/remote-config-compat",nn="@firebase/storage",sn="@firebase/storage-compat",rn="@firebase/firestore",an="@firebase/vertexai",on="@firebase/firestore-compat",cn="firebase",ln="11.1.0",un={[X]:"fire-core",[Lt]:"fire-core-compat",[kt]:"fire-analytics",[Nt]:"fire-analytics-compat",[jt]:"fire-app-check",[xt]:"fire-app-check-compat",[Ht]:"fire-auth",[Vt]:"fire-auth-compat",[Ut]:"fire-rtdb",[Wt]:"fire-data-connect",[qt]:"fire-rtdb-compat",[Kt]:"fire-fn",[Gt]:"fire-fn-compat",[zt]:"fire-iid",[Yt]:"fire-iid-compat",[Jt]:"fire-fcm",[Xt]:"fire-fcm-compat",[Qt]:"fire-perf",[Zt]:"fire-perf-compat",[en]:"fire-rc",[tn]:"fire-rc-compat",[nn]:"fire-gcs",[sn]:"fire-gcs-compat",[rn]:"fire-fst",[on]:"fire-fst-compat",[an]:"fire-vertex","fire-js":"fire-js",[cn]:"fire-js-all"};/**
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
 */const hn=new Map,dn=new Map,ge=new Map;function pe(t,e){try{t.container.addComponent(e)}catch(n){I.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,n)}}function v(t){const e=t.name;if(ge.has(e))return I.debug(`There were multiple attempts to register component ${e}.`),!1;ge.set(e,t);for(const n of hn.values())pe(n,t);for(const n of dn.values())pe(n,t);return!0}function Ne(t,e){const n=t.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),t.container.getProvider(e)}/**
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
 */const fn={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},se=new $e("app","Firebase",fn);/**
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
 */const gn=ln;function y(t,e,n){var s;let r=(s=un[t])!==null&&s!==void 0?s:t;n&&(r+=`-${n}`);const a=r.match(/\s|\//),i=e.match(/\s|\//);if(a||i){const o=[`Unable to register library "${r}" with version "${e}":`];a&&o.push(`library name "${r}" contains illegal characters (whitespace or "/")`),a&&i&&o.push("and"),i&&o.push(`version name "${e}" contains illegal characters (whitespace or "/")`),I.warn(o.join(" "));return}v(new z(`${r}-version`,()=>({library:r,version:e}),"VERSION"))}/**
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
 */const pn="firebase-heartbeat-database",mn=1,P="firebase-heartbeat-store";let V=null;function ke(){return V||(V=Le(pn,mn,{upgrade:(t,e)=>{switch(e){case 0:try{t.createObjectStore(P)}catch(n){console.warn(n)}}}}).catch(t=>{throw se.create("idb-open",{originalErrorMessage:t.message})})),V}async function bn(t){try{const n=(await ke()).transaction(P),s=await n.objectStore(P).get(xe(t));return await n.done,s}catch(e){if(e instanceof ee)I.warn(e.message);else{const n=se.create("idb-get",{originalErrorMessage:e==null?void 0:e.message});I.warn(n.message)}}}async function me(t,e){try{const s=(await ke()).transaction(P,"readwrite");await s.objectStore(P).put(e,xe(t)),await s.done}catch(n){if(n instanceof ee)I.warn(n.message);else{const s=se.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});I.warn(s.message)}}}function xe(t){return`${t.name}!${t.options.appId}`}/**
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
 */const wn=1024,yn=30*24*60*60*1e3;class In{constructor(e){this.container=e,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new En(n),this._heartbeatsCachePromise=this._storage.read().then(s=>(this._heartbeatsCache=s,s))}async triggerHeartbeat(){var e,n;try{const r=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),a=be();return((e=this._heartbeatsCache)===null||e===void 0?void 0:e.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===a||this._heartbeatsCache.heartbeats.some(i=>i.date===a)?void 0:(this._heartbeatsCache.heartbeats.push({date:a,agent:r}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(i=>{const o=new Date(i.date).valueOf();return Date.now()-o<=yn}),this._storage.overwrite(this._heartbeatsCache))}catch(s){I.warn(s)}}async getHeartbeatsHeader(){var e;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((e=this._heartbeatsCache)===null||e===void 0?void 0:e.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=be(),{heartbeatsToSend:s,unsentEntries:r}=_n(this._heartbeatsCache.heartbeats),a=Oe(JSON.stringify({version:2,heartbeats:s}));return this._heartbeatsCache.lastSentHeartbeatDate=n,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),a}catch(n){return I.warn(n),""}}}function be(){return new Date().toISOString().substring(0,10)}function _n(t,e=wn){const n=[];let s=t.slice();for(const r of t){const a=n.find(i=>i.agent===r.agent);if(a){if(a.dates.push(r.date),we(n)>e){a.dates.pop();break}}else if(n.push({agent:r.agent,dates:[r.date]}),we(n)>e){n.pop();break}s=s.slice(1)}return{heartbeatsToSend:n,unsentEntries:s}}class En{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return pt()?mt().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await bn(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(e){var n;if(await this._canUseIndexedDBPromise){const r=await this.read();return me(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:r.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var n;if(await this._canUseIndexedDBPromise){const r=await this.read();return me(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:r.lastSentHeartbeatDate,heartbeats:[...r.heartbeats,...e.heartbeats]})}else return}}function we(t){return Oe(JSON.stringify({version:2,heartbeats:t})).length}/**
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
 */function Sn(t){v(new z("platform-logger",e=>new Ft(e),"PRIVATE")),v(new z("heartbeat",e=>new In(e),"PRIVATE")),y(X,fe,t),y(X,fe,"esm2017"),y("fire-js","")}Sn("");function Tn(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function je(){try{return typeof indexedDB=="object"}catch{return!1}}function vn(){return new Promise((t,e)=>{try{let n=!0;const s="validate-browser-context-for-indexeddb-analytics-module",r=self.indexedDB.open(s);r.onsuccess=()=>{r.result.close(),n||self.indexedDB.deleteDatabase(s),t(!0)},r.onupgradeneeded=()=>{n=!1},r.onerror=()=>{var a;e(((a=r.error)===null||a===void 0?void 0:a.message)||"")}}catch(n){e(n)}})}function Cn(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const An="FirebaseError";class M extends Error{constructor(e,n,s){super(n),this.code=e,this.customData=s,this.name=An,Object.setPrototypeOf(this,M.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,L.prototype.create)}}class L{constructor(e,n,s){this.service=e,this.serviceName=n,this.errors=s}create(e,...n){const s=n[0]||{},r=`${this.service}/${e}`,a=this.errors[e],i=a?Dn(a,s):"Error",o=`${this.serviceName}: ${i} (${r}).`;return new M(r,o,s)}}function Dn(t,e){return t.replace(Mn,(n,s)=>{const r=e[s];return r!=null?String(r):`<${s}?>`})}const Mn=/\{\$([^}]+)}/g;/**
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
 */const Rn=1e3,On=2,Pn=4*60*60*1e3,$n=.5;function Q(t,e=Rn,n=On){const s=e*Math.pow(n,t),r=Math.round($n*s*(Math.random()-.5)*2);return Math.min(Pn,s+r)}/**
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
 */function He(t){return t&&t._delegate?t._delegate:t}class ${constructor(e,n,s){this.name=e,this.instanceFactory=n,this.type=s,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}const Ve="@firebase/installations",re="0.6.12";/**
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
 */const Ue=1e4,We=`w:${re}`,qe="FIS_v2",Fn="https://firebaseinstallations.googleapis.com/v1",Bn=60*60*1e3,Ln="installations",Nn="Installations";/**
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
 */const kn={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},A=new L(Ln,Nn,kn);function Ke(t){return t instanceof M&&t.code.includes("request-failed")}/**
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
 */function Ge({projectId:t}){return`${Fn}/projects/${t}/installations`}function ze(t){return{token:t.token,requestStatus:2,expiresIn:jn(t.expiresIn),creationTime:Date.now()}}async function Ye(t,e){const s=(await e.json()).error;return A.create("request-failed",{requestName:t,serverCode:s.code,serverMessage:s.message,serverStatus:s.status})}function Je({apiKey:t}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":t})}function xn(t,{refreshToken:e}){const n=Je(t);return n.append("Authorization",Hn(e)),n}async function Xe(t){const e=await t();return e.status>=500&&e.status<600?t():e}function jn(t){return Number(t.replace("s","000"))}function Hn(t){return`${qe} ${t}`}/**
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
 */async function Vn({appConfig:t,heartbeatServiceProvider:e},{fid:n}){const s=Ge(t),r=Je(t),a=e.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={fid:n,authVersion:qe,appId:t.appId,sdkVersion:We},o={method:"POST",headers:r,body:JSON.stringify(i)},c=await Xe(()=>fetch(s,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:ze(l.authToken)}}else throw await Ye("Create Installation",c)}/**
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
 */function Qe(t){return new Promise(e=>{setTimeout(e,t)})}/**
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
 */function Un(t){return btoa(String.fromCharCode(...t)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Wn=/^[cdef][\w-]{21}$/,Z="";function qn(){try{const t=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(t),t[0]=112+t[0]%16;const n=Kn(t);return Wn.test(n)?n:Z}catch{return Z}}function Kn(t){return Un(t).substr(0,22)}/**
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
 */function N(t){return`${t.appName}!${t.appId}`}/**
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
 */const Ze=new Map;function et(t,e){const n=N(t);tt(n,e),Gn(n,e)}function tt(t,e){const n=Ze.get(t);if(n)for(const s of n)s(e)}function Gn(t,e){const n=zn();n&&n.postMessage({key:t,fid:e}),Yn()}let C=null;function zn(){return!C&&"BroadcastChannel"in self&&(C=new BroadcastChannel("[Firebase] FID Change"),C.onmessage=t=>{tt(t.data.key,t.data.fid)}),C}function Yn(){Ze.size===0&&C&&(C.close(),C=null)}/**
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
 */const Jn="firebase-installations-database",Xn=1,D="firebase-installations-store";let U=null;function ae(){return U||(U=Le(Jn,Xn,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(D)}}})),U}async function B(t,e){const n=N(t),r=(await ae()).transaction(D,"readwrite"),a=r.objectStore(D),i=await a.get(n);return await a.put(e,n),await r.done,(!i||i.fid!==e.fid)&&et(t,e.fid),e}async function nt(t){const e=N(t),s=(await ae()).transaction(D,"readwrite");await s.objectStore(D).delete(e),await s.done}async function k(t,e){const n=N(t),r=(await ae()).transaction(D,"readwrite"),a=r.objectStore(D),i=await a.get(n),o=e(i);return o===void 0?await a.delete(n):await a.put(o,n),await r.done,o&&(!i||i.fid!==o.fid)&&et(t,o.fid),o}/**
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
 */async function ie(t){let e;const n=await k(t.appConfig,s=>{const r=Qn(s),a=Zn(t,r);return e=a.registrationPromise,a.installationEntry});return n.fid===Z?{installationEntry:await e}:{installationEntry:n,registrationPromise:e}}function Qn(t){const e=t||{fid:qn(),registrationStatus:0};return st(e)}function Zn(t,e){if(e.registrationStatus===0){if(!navigator.onLine){const r=Promise.reject(A.create("app-offline"));return{installationEntry:e,registrationPromise:r}}const n={fid:e.fid,registrationStatus:1,registrationTime:Date.now()},s=es(t,n);return{installationEntry:n,registrationPromise:s}}else return e.registrationStatus===1?{installationEntry:e,registrationPromise:ts(t)}:{installationEntry:e}}async function es(t,e){try{const n=await Vn(t,e);return B(t.appConfig,n)}catch(n){throw Ke(n)&&n.customData.serverCode===409?await nt(t.appConfig):await B(t.appConfig,{fid:e.fid,registrationStatus:0}),n}}async function ts(t){let e=await ye(t.appConfig);for(;e.registrationStatus===1;)await Qe(100),e=await ye(t.appConfig);if(e.registrationStatus===0){const{installationEntry:n,registrationPromise:s}=await ie(t);return s||n}return e}function ye(t){return k(t,e=>{if(!e)throw A.create("installation-not-found");return st(e)})}function st(t){return ns(t)?{fid:t.fid,registrationStatus:0}:t}function ns(t){return t.registrationStatus===1&&t.registrationTime+Ue<Date.now()}/**
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
 */async function ss({appConfig:t,heartbeatServiceProvider:e},n){const s=rs(t,n),r=xn(t,n),a=e.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={installation:{sdkVersion:We,appId:t.appId}},o={method:"POST",headers:r,body:JSON.stringify(i)},c=await Xe(()=>fetch(s,o));if(c.ok){const l=await c.json();return ze(l)}else throw await Ye("Generate Auth Token",c)}function rs(t,{fid:e}){return`${Ge(t)}/${e}/authTokens:generate`}/**
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
 */async function oe(t,e=!1){let n;const s=await k(t.appConfig,a=>{if(!rt(a))throw A.create("not-registered");const i=a.authToken;if(!e&&os(i))return a;if(i.requestStatus===1)return n=as(t,e),a;{if(!navigator.onLine)throw A.create("app-offline");const o=ls(a);return n=is(t,o),o}});return n?await n:s.authToken}async function as(t,e){let n=await Ie(t.appConfig);for(;n.authToken.requestStatus===1;)await Qe(100),n=await Ie(t.appConfig);const s=n.authToken;return s.requestStatus===0?oe(t,e):s}function Ie(t){return k(t,e=>{if(!rt(e))throw A.create("not-registered");const n=e.authToken;return us(n)?Object.assign(Object.assign({},e),{authToken:{requestStatus:0}}):e})}async function is(t,e){try{const n=await ss(t,e),s=Object.assign(Object.assign({},e),{authToken:n});return await B(t.appConfig,s),n}catch(n){if(Ke(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await nt(t.appConfig);else{const s=Object.assign(Object.assign({},e),{authToken:{requestStatus:0}});await B(t.appConfig,s)}throw n}}function rt(t){return t!==void 0&&t.registrationStatus===2}function os(t){return t.requestStatus===2&&!cs(t)}function cs(t){const e=Date.now();return e<t.creationTime||t.creationTime+t.expiresIn<e+Bn}function ls(t){const e={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},t),{authToken:e})}function us(t){return t.requestStatus===1&&t.requestTime+Ue<Date.now()}/**
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
 */async function hs(t){const e=t,{installationEntry:n,registrationPromise:s}=await ie(e);return s?s.catch(console.error):oe(e).catch(console.error),n.fid}/**
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
 */async function ds(t,e=!1){const n=t;return await fs(n),(await oe(n,e)).token}async function fs(t){const{registrationPromise:e}=await ie(t);e&&await e}/**
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
 */function gs(t){if(!t||!t.options)throw W("App Configuration");if(!t.name)throw W("App Name");const e=["projectId","apiKey","appId"];for(const n of e)if(!t.options[n])throw W(n);return{appName:t.name,projectId:t.options.projectId,apiKey:t.options.apiKey,appId:t.options.appId}}function W(t){return A.create("missing-app-config-values",{valueName:t})}/**
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
 */const at="installations",ps="installations-internal",ms=t=>{const e=t.getProvider("app").getImmediate(),n=gs(e),s=Ne(e,"heartbeat");return{app:e,appConfig:n,heartbeatServiceProvider:s,_delete:()=>Promise.resolve()}},bs=t=>{const e=t.getProvider("app").getImmediate(),n=Ne(e,at).getImmediate();return{getId:()=>hs(n),getToken:r=>ds(n,r)}};function ws(){v(new $(at,ms,"PUBLIC")),v(new $(ps,bs,"PRIVATE"))}ws();y(Ve,re);y(Ve,re,"esm2017");/**
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
 */const _e="analytics",ys="firebase_id",Is="origin",_s=60*1e3,Es="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ce="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new te("@firebase/analytics");/**
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
 */const Ss={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},b=new L("analytics","Analytics",Ss);/**
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
 */function Ts(t){if(!t.startsWith(ce)){const e=b.create("invalid-gtag-resource",{gtagURL:t});return m.warn(e.message),""}return t}function it(t){return Promise.all(t.map(e=>e.catch(n=>n)))}function vs(t,e){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(t,e)),n}function Cs(t,e){const n=vs("firebase-js-sdk-policy",{createScriptURL:Ts}),s=document.createElement("script"),r=`${ce}?l=${t}&id=${e}`;s.src=n?n==null?void 0:n.createScriptURL(r):r,s.async=!0,document.head.appendChild(s)}function As(t){let e=[];return Array.isArray(window[t])?e=window[t]:window[t]=e,e}async function Ds(t,e,n,s,r,a){const i=s[r];try{if(i)await e[i];else{const c=(await it(n)).find(l=>l.measurementId===r);c&&await e[c.appId]}}catch(o){m.error(o)}t("config",r,a)}async function Ms(t,e,n,s,r){try{let a=[];if(r&&r.send_to){let i=r.send_to;Array.isArray(i)||(i=[i]);const o=await it(n);for(const c of i){const l=o.find(h=>h.measurementId===c),d=l&&e[l.appId];if(d)a.push(d);else{a=[];break}}}a.length===0&&(a=Object.values(e)),await Promise.all(a),t("event",s,r||{})}catch(a){m.error(a)}}function Rs(t,e,n,s){async function r(a,...i){try{if(a==="event"){const[o,c]=i;await Ms(t,e,n,o,c)}else if(a==="config"){const[o,c]=i;await Ds(t,e,n,s,o,c)}else if(a==="consent"){const[o,c]=i;t("consent",o,c)}else if(a==="get"){const[o,c,l]=i;t("get",o,c,l)}else if(a==="set"){const[o]=i;t("set",o)}else t(a,...i)}catch(o){m.error(o)}}return r}function Os(t,e,n,s,r){let a=function(...i){window[s].push(arguments)};return window[r]&&typeof window[r]=="function"&&(a=window[r]),window[r]=Rs(a,t,e,n),{gtagCore:a,wrappedGtag:window[r]}}function Ps(t){const e=window.document.getElementsByTagName("script");for(const n of Object.values(e))if(n.src&&n.src.includes(ce)&&n.src.includes(t))return n;return null}/**
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
 */const $s=30,Fs=1e3;class Bs{constructor(e={},n=Fs){this.throttleMetadata=e,this.intervalMillis=n}getThrottleMetadata(e){return this.throttleMetadata[e]}setThrottleMetadata(e,n){this.throttleMetadata[e]=n}deleteThrottleMetadata(e){delete this.throttleMetadata[e]}}const ot=new Bs;function Ls(t){return new Headers({Accept:"application/json","x-goog-api-key":t})}async function Ns(t){var e;const{appId:n,apiKey:s}=t,r={method:"GET",headers:Ls(s)},a=Es.replace("{app-id}",n),i=await fetch(a,r);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((e=c.error)===null||e===void 0)&&e.message&&(o=c.error.message)}catch{}throw b.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function ks(t,e=ot,n){const{appId:s,apiKey:r,measurementId:a}=t.options;if(!s)throw b.create("no-app-id");if(!r){if(a)return{measurementId:a,appId:s};throw b.create("no-api-key")}const i=e.getThrottleMetadata(s)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new Hs;return setTimeout(async()=>{o.abort()},_s),ct({appId:s,apiKey:r,measurementId:a},i,o,e)}async function ct(t,{throttleEndTimeMillis:e,backoffCount:n},s,r=ot){var a;const{appId:i,measurementId:o}=t;try{await xs(s,e)}catch(c){if(o)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await Ns(t);return r.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!js(l)){if(r.deleteThrottleMetadata(i),o)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const d=Number((a=l==null?void 0:l.customData)===null||a===void 0?void 0:a.httpStatus)===503?Q(n,r.intervalMillis,$s):Q(n,r.intervalMillis),h={throttleEndTimeMillis:Date.now()+d,backoffCount:n+1};return r.setThrottleMetadata(i,h),m.debug(`Calling attemptFetch again in ${d} millis`),ct(t,h,s,r)}}function xs(t,e){return new Promise((n,s)=>{const r=Math.max(e-Date.now(),0),a=setTimeout(n,r);t.addEventListener(()=>{clearTimeout(a),s(b.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function js(t){if(!(t instanceof M)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class Hs{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}async function Vs(t,e,n,s,r){if(r&&r.global){t("event",n,s);return}else{const a=await e,i=Object.assign(Object.assign({},s),{send_to:a});t("event",n,i)}}/**
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
 */async function Us(){if(je())try{await vn()}catch(t){return m.warn(b.create("indexeddb-unavailable",{errorInfo:t==null?void 0:t.toString()}).message),!1}else return m.warn(b.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Ws(t,e,n,s,r,a,i){var o;const c=ks(t);c.then(g=>{n[g.measurementId]=g.appId,t.options.measurementId&&g.measurementId!==t.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${t.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>m.error(g)),e.push(c);const l=Us().then(g=>{if(g)return s.getId()}),[d,h]=await Promise.all([c,l]);Ps(a)||Cs(a,d.measurementId),r("js",new Date);const f=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return f[Is]="firebase",f.update=!0,h!=null&&(f[ys]=h),r("config",d.measurementId,f),d.measurementId}/**
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
 */class qs{constructor(e){this.app=e}_delete(){return delete O[this.app.options.appId],Promise.resolve()}}let O={},Ee=[];const Se={};let q="dataLayer",Ks="gtag",Te,lt,ve=!1;function Gs(){const t=[];if(Tn()&&t.push("This is a browser extension environment."),Cn()||t.push("Cookies are not available."),t.length>0){const e=t.map((s,r)=>`(${r+1}) ${s}`).join(" "),n=b.create("invalid-analytics-context",{errorInfo:e});m.warn(n.message)}}function zs(t,e,n){Gs();const s=t.options.appId;if(!s)throw b.create("no-app-id");if(!t.options.apiKey)if(t.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${t.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw b.create("no-api-key");if(O[s]!=null)throw b.create("already-exists",{id:s});if(!ve){As(q);const{wrappedGtag:a,gtagCore:i}=Os(O,Ee,Se,q,Ks);lt=a,Te=i,ve=!0}return O[s]=Ws(t,Ee,Se,e,Te,q,n),new qs(t)}function Ys(t,e,n,s){t=He(t),Vs(lt,O[t.app.options.appId],e,n,s).catch(r=>m.error(r))}const Ce="@firebase/analytics",Ae="0.10.11";function Js(){v(new $(_e,(e,{options:n})=>{const s=e.getProvider("app").getImmediate(),r=e.getProvider("installations-internal").getImmediate();return zs(s,r,n)},"PUBLIC")),v(new $("analytics-internal",t,"PRIVATE")),y(Ce,Ae),y(Ce,Ae,"esm2017");function t(e){try{const n=e.getProvider(_e).getImmediate();return{logEvent:(s,r,a)=>Ys(n,s,r,a)}}catch(n){throw b.create("interop-component-reg-failed",{reason:n})}}}Js();const K="@firebase/remote-config",De="0.5.0";/**
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
 */const Xs="remote-config",Me=100;/**
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
 */const Qs={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},p=new L("remoteconfig","Remote Config",Qs);function Zs(t){const e=He(t);return e._initializePromise||(e._initializePromise=e._storageCache.loadFromStorage().then(()=>{e._isInitializationComplete=!0})),e._initializePromise}/**
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
 */class er{constructor(e,n,s,r){this.client=e,this.storage=n,this.storageCache=s,this.logger=r}isCachedDataFresh(e,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const s=Date.now()-n,r=s<=e;return this.logger.debug(`Config fetch cache check. Cache age millis: ${s}. Cache max age millis (minimumFetchIntervalMillis setting): ${e}. Is cache hit: ${r}.`),r}async fetch(e){const[n,s]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(s&&this.isCachedDataFresh(e.cacheMaxAgeMillis,n))return s;e.eTag=s&&s.eTag;const r=await this.client.fetch(e),a=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return r.status===200&&a.push(this.storage.setLastSuccessfulFetchResponse(r)),await Promise.all(a),r}}/**
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
 */function tr(t=navigator){return t.languages&&t.languages[0]||t.language}/**
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
 */class nr{constructor(e,n,s,r,a,i){this.firebaseInstallations=e,this.sdkVersion=n,this.namespace=s,this.projectId=r,this.apiKey=a,this.appId=i}async fetch(e){const[n,s]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),a=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":e.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:s,app_id:this.appId,language_code:tr(),custom_signals:e.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(a,c),d=new Promise((w,E)=>{e.signal.addEventListener(()=>{const le=new Error("The operation was aborted.");le.name="AbortError",E(le)})});let h;try{await Promise.race([l,d]),h=await l}catch(w){let E="fetch-client-network";throw(w==null?void 0:w.name)==="AbortError"&&(E="fetch-timeout"),p.create(E,{originalErrorMessage:w==null?void 0:w.message})}let f=h.status;const g=h.headers.get("ETag")||void 0;let _,R;if(h.status===200){let w;try{w=await h.json()}catch(E){throw p.create("fetch-client-parse",{originalErrorMessage:E==null?void 0:E.message})}_=w.entries,R=w.state}if(R==="INSTANCE_STATE_UNSPECIFIED"?f=500:R==="NO_CHANGE"?f=304:(R==="NO_TEMPLATE"||R==="EMPTY_CONFIG")&&(_={}),f!==304&&f!==200)throw p.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:_}}}/**
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
 */function sr(t,e){return new Promise((n,s)=>{const r=Math.max(e-Date.now(),0),a=setTimeout(n,r);t.addEventListener(()=>{clearTimeout(a),s(p.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function rr(t){if(!(t instanceof M)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class ar{constructor(e,n){this.client=e,this.storage=n}async fetch(e){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(e,n)}async attemptFetch(e,{throttleEndTimeMillis:n,backoffCount:s}){await sr(e.signal,n);try{const r=await this.client.fetch(e);return await this.storage.deleteThrottleMetadata(),r}catch(r){if(!rr(r))throw r;const a={throttleEndTimeMillis:Date.now()+Q(s),backoffCount:s+1};return await this.storage.setThrottleMetadata(a),this.attemptFetch(e,a)}}}/**
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
 */const ir=60*1e3,or=12*60*60*1e3;class cr{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(e,n,s,r,a){this.app=e,this._client=n,this._storageCache=s,this._storage=r,this._logger=a,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:ir,minimumFetchIntervalMillis:or},this.defaultConfig={}}}/**
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
 */function F(t,e){const n=t.target.error||void 0;return p.create(e,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const S="app_namespace_store",lr="firebase_remote_config",ur=1;function hr(){return new Promise((t,e)=>{try{const n=indexedDB.open(lr,ur);n.onerror=s=>{e(F(s,"storage-open"))},n.onsuccess=s=>{t(s.target.result)},n.onupgradeneeded=s=>{const r=s.target.result;switch(s.oldVersion){case 0:r.createObjectStore(S,{keyPath:"compositeKey"})}}}catch(n){e(p.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class dr{constructor(e,n,s,r=hr()){this.appId=e,this.appName=n,this.namespace=s,this.openDbPromise=r}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(e){return this.set("last_fetch_status",e)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(e){return this.set("last_successful_fetch_timestamp_millis",e)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(e){return this.set("last_successful_fetch_response",e)}getActiveConfig(){return this.get("active_config")}setActiveConfig(e){return this.set("active_config",e)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(e){return this.set("active_config_etag",e)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(e){return this.set("throttle_metadata",e)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}async setCustomSignals(e){const s=(await this.openDbPromise).transaction([S],"readwrite"),r=await this.getWithTransaction("custom_signals",s),a=Object.assign(Object.assign({},r),e),i=Object.fromEntries(Object.entries(a).filter(([o,c])=>c!==null).map(([o,c])=>typeof c=="number"?[o,c.toString()]:[o,c]));if(Object.keys(i).length>Me)throw p.create("custom-signal-max-allowed-signals",{maxSignals:Me});return await this.setWithTransaction("custom_signals",i,s),i}async getWithTransaction(e,n){return new Promise((s,r)=>{const a=n.objectStore(S),i=this.createCompositeKey(e);try{const o=a.get(i);o.onerror=c=>{r(F(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;s(l?l.value:void 0)}}catch(o){r(p.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async setWithTransaction(e,n,s){return new Promise((r,a)=>{const i=s.objectStore(S),o=this.createCompositeKey(e);try{const c=i.put({compositeKey:o,value:n});c.onerror=l=>{a(F(l,"storage-set"))},c.onsuccess=()=>{r()}}catch(c){a(p.create("storage-set",{originalErrorMessage:c==null?void 0:c.message}))}})}async get(e){const s=(await this.openDbPromise).transaction([S],"readonly");return this.getWithTransaction(e,s)}async set(e,n){const r=(await this.openDbPromise).transaction([S],"readwrite");return this.setWithTransaction(e,n,r)}async delete(e){const n=await this.openDbPromise;return new Promise((s,r)=>{const i=n.transaction([S],"readwrite").objectStore(S),o=this.createCompositeKey(e);try{const c=i.delete(o);c.onerror=l=>{r(F(l,"storage-delete"))},c.onsuccess=()=>{s()}}catch(c){r(p.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(e){return[this.appId,this.appName,this.namespace,e].join()}}/**
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
 */class fr{constructor(e){this.storage=e}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const e=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),s=this.storage.getActiveConfig(),r=this.storage.getCustomSignals(),a=await e;a&&(this.lastFetchStatus=a);const i=await n;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await s;o&&(this.activeConfig=o);const c=await r;c&&(this.customSignals=c)}setLastFetchStatus(e){return this.lastFetchStatus=e,this.storage.setLastFetchStatus(e)}setLastSuccessfulFetchTimestampMillis(e){return this.lastSuccessfulFetchTimestampMillis=e,this.storage.setLastSuccessfulFetchTimestampMillis(e)}setActiveConfig(e){return this.activeConfig=e,this.storage.setActiveConfig(e)}async setCustomSignals(e){this.customSignals=await this.storage.setCustomSignals(e)}}/**
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
 */function gr(){v(new $(Xs,t,"PUBLIC").setMultipleInstances(!0)),y(K,De),y(K,De,"esm2017");function t(e,{instanceIdentifier:n}){const s=e.getProvider("app").getImmediate(),r=e.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw p.create("registration-window");if(!je())throw p.create("indexed-db-unavailable");const{projectId:a,apiKey:i,appId:o}=s.options;if(!a)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!o)throw p.create("registration-app-id");n=n||"firebase";const c=new dr(o,s.name,n),l=new fr(c),d=new te(K);d.logLevel=u.ERROR;const h=new nr(r,gn,n,a,i,o),f=new ar(h,c),g=new er(f,c,l,d),_=new cr(s,g,l,c,d);return Zs(_),_}}gr();const pr=t=>Object.fromEntries(new URLSearchParams(t)),mr=()=>{const t=ut(),e=pr(t.search);return"utm_campaign"in e&&"utm_medium"in e&&"utm_source"in e?{traffic_campaign:e.utm_campaign,traffic_medium:e.utm_medium,traffic_source:e.utm_source}:{}},Er=()=>{const[t,e]=G.useState({});return G.useEffect(()=>{const n=setInterval(()=>{},1e3);return()=>clearInterval(n)},[]),t},Sr=()=>{const t=mr();return{logEvent:G.useCallback((n,s)=>{},[t])}};export{Er as a,Sr as u};
