#!/usr/bin/env bash
#
# flakecheck.sh — Run a Cypress e2e spec repeatedly to gauge flakiness.
#
# Default Cypress command:
#   yarn cypress run --e2e --browser chrome --config-file cypress/cypress.config.ts
#
# Usage:
#   ./scripts/flakecheck.sh -s <spec> [-n <runs>] [-t "<test title>"] [-b <browser>] [--headed] [--keep-artifacts]
#
# Examples:
#   # Spec-only, 25 runs
#   ./scripts/flakecheck.sh -s cypress/e2e/oaIndividualOffer.cy.ts -n 25
#
#   # Single test case within the spec (via `@cypress/gre`), 50 runs
#   ./scripts/flakecheck.sh -s cypress/e2e/oaIndividualOffer.cy.ts -t "I should be able to create an individual offer (event)" -n 50
#
#   # Different browser
#   ./scripts/flakecheck.sh -s cypress/e2e/oaIndividualOffer.cy.ts -n 30 -b electron

set -euo pipefail

spec=""
runs=20
test_title=""
browser="chrome"
config_file="cypress/cypress.config.ts"
headed="false"
keep_artifacts="false"
dry_run="false"

print_usage() {
  cat <<EOF
Usage:
  $(basename "$0") -s <spec> [-n <runs>] [-t "<test title>"] [-b <browser>] [--headed] [--keep-artifacts]

Options:
  -s <spec>             Path to spec file (required), e.g. cypress/e2e/login.cy.ts
  -n <runs>             Number of runs (default: ${runs})
  -t "<test title>"     Single test name to run (requires cypress-grep)
  -b <browser>          Cypress browser (default: ${browser})
  --headed              Run headed
  --keep-artifacts      Keep per-run video/screenshots (default: deleted)
  --dry-run             Only print the commands that would run; do not execute Cypress
  -h, --help            Show help
EOF
}

while (( "$#" )); do
  case "$1" in
    -s) spec="$2"; shift 2 ;;
    -n) runs="$2"; shift 2 ;;
    -t) test_title="$2"; shift 2 ;;
    -b) browser="$2"; shift 2 ;;
    --headed) headed="true"; shift ;;
    --keep-artifacts) keep_artifacts="true"; shift ;;
  --dry-run) dry_run="true"; shift ;;
    -h|--help) print_usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; print_usage; exit 1 ;;
  esac
done

if [[ -z "$spec" ]]; then
  echo "Error: -s <spec> is required" >&2
  print_usage
  exit 1
fi

if [[ ! -f "$spec" ]]; then
  echo "Error: spec not found: $spec" >&2
  exit 1
fi

if ! command -v yarn >/dev/null 2>&1; then
  echo "Error: yarn not found." >&2
  exit 1
fi

timestamp() {
  # Returns current epoch time in milliseconds.
  # Tries GNU date first (Linux / coreutils), then falls back to perl, python, or POSIX seconds * 1000.
  if command -v date >/dev/null 2>&1; then
    # GNU date supports %N (nanoseconds). On macOS/BSD this prints literal %N or errors.
    local maybe_ms
    maybe_ms="$(date +%s%3N 2>/dev/null || true)"
    if [[ "$maybe_ms" =~ ^[0-9]+$ ]]; then
      echo "$maybe_ms"
      return 0
    fi
  fi

  if command -v perl >/dev/null 2>&1; then
    perl -MTime::HiRes=time -e 'printf("%.0f\n", time()*1000)'
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'EOF'
import time; print(int(time.time()*1000))
EOF
    return 0
  fi

  # Last‑ditch: seconds precision only.
  echo $(( $(date +%s) * 1000 ))
}
human_ms() { # ms -> "Xs Yms"
  local ms="$1"
  local s=$(( ms / 1000 ))
  local rem=$(( ms % 1000 ))
  printf "%ds %dms" "$s" "$rem"
}

tmp_root="$(mktemp -d -t flakecheck.XXXXXX)"
log_dir="${tmp_root}/logs"
artifacts_dir="${tmp_root}/artifacts"
mkdir -p "$log_dir" "$artifacts_dir"

passes=0
fails=0
declare -a durations_ms=()
declare -a fail_runs=()

echo "== Flakecheck =="
echo "Spec:            $spec"
if [[ -n "$test_title" ]]; then
  echo "Test title:      $test_title"
  # Warn if @cypress/grep (plugin) might be missing (best-effort heuristic)
  if ! grep -R "@cypress/grep" --quiet package.json 2>/dev/null; then
    echo "(note) '-t' provided but '@cypress/grep' not detected in package.json; the filter may be ignored." >&2
  fi
fi
echo "Runs:            $runs"
echo "Browser:         $browser"
echo "Config file:     $config_file"
echo "Headed:          $headed"
echo "Artifacts:       $( [[ "$keep_artifacts" == "true" ]] && echo keep || echo delete )"
echo "Dry run:         $dry_run"
echo "Work dir:        $tmp_root"
echo

for i in $(seq 1 "$runs"); do
  run_id=$(printf "%03d" "$i")
  start_ms="$(timestamp)"

  cmd=(yarn cypress run
    --e2e
    --browser "$browser"
    --config-file "$config_file"
    --spec "$spec"
    --config "retries=0,video=${keep_artifacts}"
  )

  if [[ "$headed" == "true" ]]; then
    cmd+=(--headed)
  fi

  # If using cypress-grep to target a specific test
  if [[ -n "$test_title" ]]; then
    cmd+=(--env "grep=${test_title}")
  fi

  log_file="${log_dir}/run_${run_id}.log"

  echo "-- Run ${run_id}/${runs} ---------------------------------------------"
  echo "Command: ${cmd[*]}"
  if [[ "$dry_run" == "true" ]]; then
    echo "(dry-run) Skipping execution; writing command to $log_file"
    printf "DRY RUN COMMAND: %s\n" "${cmd[*]}" >"$log_file"
    exit_code=0
  else
    set +e
    "${cmd[@]}" >"$log_file" 2>&1
    exit_code=$?
    set -e
  fi

  end_ms="$(timestamp)"
  dur=$(( end_ms - start_ms ))
  durations_ms+=( "$dur" )

  if [[ "$exit_code" -eq 0 ]]; then
    ((passes++))
    echo "Result: PASS in $(human_ms "$dur")"
  else
    ((fails++))
    fail_runs+=( "$run_id" )
    echo "Result: FAIL in $(human_ms "$dur") (exit=$exit_code)"
  fi

  # Move artifacts if kept
  if [[ "$keep_artifacts" == "true" ]]; then
    # Cypress defaults: cypress/videos, cypress/screenshots
    run_art_dir="${artifacts_dir}/run_${run_id}"
    mkdir -p "$run_art_dir"
    if [[ -d cypress/videos ]]; then
      cp -R cypress/videos "${run_art_dir}/videos" || true
      rm -rf cypress/videos || true
    fi
    if [[ -d cypress/screenshots ]]; then
      cp -R cypress/screenshots "${run_art_dir}/screenshots" || true
      rm -rf cypress/screenshots || true
    fi
  else
  [[ -d cypress/videos ]] && rm -rf cypress/videos || true
  [[ -d cypress/screenshots ]] && rm -rf cypress/screenshots || true
  fi
done

# Stats
total="$runs"
pass_rate=$(awk -v p="$passes" -v t="$total" 'BEGIN { if (t==0) print 0; else printf "%.2f", (p/t)*100 }')
fail_rate=$(awk -v f="$fails" -v t="$total" 'BEGIN { if (t==0) print 0; else printf "%.2f", (f/t)*100 }')

# Mean
sum_ms=$(printf "%s\n" "${durations_ms[@]}" | awk '{s+=$1} END{print s+0}')
mean_ms=$(awk -v s="$sum_ms" -v t="$total" 'BEGIN { if (t==0) print 0; else printf "%.0f", s/t }')

# p95 (nearest-rank)
sorted_ms=($(printf "%s\n" "${durations_ms[@]}" | sort -n))
rank=$(( (95 * total + 99) / 100 )) # ceil(0.95*N)
(( rank < 1 )) && rank=1
(( rank > total )) && rank="$total"
p95_ms="${sorted_ms[$((rank-1))]}"

echo
echo "== Summary =="
echo "Spec:            $spec"
[[ -n "$test_title" ]] && echo "Test title:      $test_title"
echo "Runs:            $total"
echo "Passes:          $passes"
echo "Fails:           $fails"
echo "Pass rate:       ${pass_rate}%"
echo "Fail rate:       ${fail_rate}%"
echo "Mean duration:   $(human_ms "$mean_ms")"
echo "p95 duration:    $(human_ms "$p95_ms")"
if (( fails > 0 )); then
  echo "Failed runs:     ${fail_runs[*]}"
fi
echo "Logs dir:        $log_dir"
echo "Artifacts dir:   $artifacts_dir"
echo
echo "Tip:"
echo "  - Use --keep-artifacts and inspect per-run videos/screenshots."
echo "  - To target a single test, install cypress-grep and pass -t \"<test name>\"."
